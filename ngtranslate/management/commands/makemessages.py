# -*- coding: utf-8 -*-
import os
import io
import re
from functools import total_ordering
from itertools import repeat

from django.conf import settings
from django.utils.six import StringIO
from django.core.management.base import CommandError
from django.core.management.commands import makemessages
from django.utils.translation.trans_real import blankout

NO_LOCALE_DIR = object()


def djangularize(src, origin=None):
    out = StringIO('')
    offset = 0
    directive_re = re.compile(r'<(?P<tag_name>\w+)[-=\/\"\'\s\w]*'
                              r'(dj-translatable)[-=\/\"\'\s\w]*\/?>',
                              re.IGNORECASE | re.DOTALL | re.VERBOSE)
    for match in directive_re.finditer(src):
        msg = None
        msg_out = None
        msg_length = 0
        tag_str = repr(match.group())
        out.write(blankout(src[offset:match.start()], 'X'))
        offset = match.start()
        is_closed_tag = ((re.search(r'\/>', tag_str)) is not None)
        trans_attribute = re.search(r'dj-translatable\s*=\s*\"'
                                    r'(?P<attr_name>[-\w\s]+)\"', tag_str)
        if trans_attribute:
            trans_attr_name = trans_attribute.group('attr_name').strip()
            attr_val_re = r''.join([trans_attr_name,
                                    r'\s*=\s*\"(?P<attr_value>[\w\s]+)\"'])
            attr_value = re.search(attr_val_re, tag_str)
            if attr_value:
                msg = attr_value.group('attr_value').strip()
                msg_out = ' gettext(%r) ' % msg
                msg_length = len(msg_out)
                out.write(msg_out)
        if not is_closed_tag:
            tag_name = match.group('tag_name')
            tag_closer_re = re.compile(r'<\/%s>' % tag_name)
            tag_closer = tag_closer_re.search(src, match.end())
            if tag_closer:
                msg = src[match.end():tag_closer.start()]
                msg_out = ' gettext(%r) ' % msg
                msg_length += len(msg_out)
                out.write(msg_out)
        delta = len(tag_str) - msg_length
        if delta > 0:
            out.write(''.join(repeat('X', delta)))
        offset += len(tag_str)
    return out.getvalue()


@total_ordering
class DjangularTranslatableFile(makemessages.TranslatableFile):

    def process(self, command, domain):
        """
        Override django TranslatableFile behavior for adding djangular domain
        """
        file_ext = os.path.splitext(self.file)[1]
        if domain == 'djangular' and file_ext != '.py':
            orig_file = os.path.join(self.dirpath, self.file)
            work_file = orig_file
            with io.open(orig_file, encoding=settings.FILE_CHARSET) as fp:
                src_data = fp.read()
            content = djangularize(src_data, orig_file[2:])
            work_file = os.path.join(self.dirpath, '%s.py' % self.file)
            with io.open(work_file, "w", encoding='utf-8') as fp:
                fp.write(unicode(content))
            args = [
                'xgettext',
                '-d', domain,
                '--language=Python',
                '--keyword=gettext_noop',
                '--keyword=gettext_lazy',
                '--keyword=ngettext_lazy:1,2',
                '--keyword=ugettext_noop',
                '--keyword=ugettext_lazy',
                '--keyword=ungettext_lazy:1,2',
                '--keyword=pgettext:1c,2',
                '--keyword=npgettext:1c,2,3',
                '--keyword=pgettext_lazy:1c,2',
                '--keyword=npgettext_lazy:1c,2,3',
                '--output=-'
            ] + command.xgettext_options
            args.append(work_file)
            msgs, errors, status = makemessages.gettext_popen_wrapper(args)
            if errors:
                if status != makemessages.STATUS_OK:
                    os.unlink(work_file)
                    raise CommandError(
                        "errors happened while running xgettext on %s\n%s" %
                        (self.file, errors))
                elif command.verbosity > 0:
                    # Print warnings
                    command.stdout.write(errors)
            if msgs:
                # Write/append messages to pot file
                if self.locale_dir is NO_LOCALE_DIR:
                    file_path = os.path.normpath(os.path.join(self.dirpath,
                                                              self.file))
                    raise CommandError(
                        "Unable to find a locale path to store"
                        " translations for file %s" % file_path)
                potfile = os.path.join(self.locale_dir, '%s.pot' % str(domain))
                # Remove '.py' suffix
                if os.name == 'nt':
                    # Preserve '.\' prefix on Windows to respect gettext behavior
                    old = '#: ' + work_file
                    new = '#: ' + orig_file
                else:
                    old = '#: ' + work_file[2:]
                    new = '#: ' + orig_file[2:]
                msgs = msgs.replace(old, new)
                makemessages.write_pot_file(potfile, msgs)
            os.unlink(work_file)
        else:
            super(DjangularTranslatableFile,
                  self).process(command, domain)


class Command(makemessages.Command):
    def handle(self, *args, **kwargs):
        self.is_djangular = False
        if kwargs.get('domain') == 'djangular':
            self.is_djangular = True
            kwargs['domain'] = 'django'
        super(Command, self).handle(*args, **kwargs)

    def find_files(self, root):
        files = super(Command, self).find_files(root)
        if self.is_djangular:
            for idx, _file in enumerate(files):
                if isinstance(_file, makemessages.TranslatableFile):
                    files[idx] = DjangularTranslatableFile(_file.dirpath,
                                                           _file.file,
                                                           _file.locale_dir)
        return files

    def build_potfiles(self):
        if self.is_djangular:
            self.domain = 'djangular'
        return makemessages.Command.build_potfiles(self)
