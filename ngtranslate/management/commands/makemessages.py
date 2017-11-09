# -*- coding: utf-8 -*-
import io
import os
import re
from django.conf import settings
from django.core.files.temp import NamedTemporaryFile
from django.core.management.base import CommandError
from django.core.management.commands import makemessages
from django.core.management.commands.makemessages import (write_pot_file,
                                                          STATUS_OK)
from django.core.management.utils import popen_wrapper
from django.utils.functional import cached_property

NO_LOCALE_DIR = object()


class AngularBuildFile(makemessages.BuildFile):
    def __init__(self, command, domain, translatable):
        super().__init__(command, domain, translatable)

    @cached_property
    def is_templatized(self):
        if self.domain is not 'djangular':
            return super().is_templatized
        return True

    @cached_property
    def work_path(self):
        """
        Path to a file which is being fed into GNU gettext pipeline. This may
        be either a translatable or its preprocessed version.
        """
        if self.domain is not 'djangular':
            return super().work_path

        if not self.is_templatized:
            return self.path

        filename = '%s.%s' % (self.translatable.file, 'py')
        return os.path.join(self.translatable.dirpath, filename)

    def custom_preprocess(self):
        """
        Preprocess (if necessary) a translatable file before passing it to
        xgettext GNU gettext utility.
        """
        with io.open(self.path, 'r', encoding=settings.FILE_CHARSET) as fp:
            src_data = fp.read()

        if self.domain == 'djangular':
            content = self.process(src_data)

        with io.open(self.work_path, 'w', encoding='utf-8') as fp:
            fp.write(content)

    def preprocess(self):
        if self.domain == 'djangular':
            self.custom_preprocess()
        else:
            super().preprocess()

    def process(self, src_data):
        if not src_data:
            return src_data

        regex = r"""{{\s*'(.*)'\s*\|\s*translate\s*}}"""
        texts = re.compile(regex).findall(src_data)
        return "\n".join(["_('{}')".format(text) for text in texts])


class Command(makemessages.Command):
    build_file_class = AngularBuildFile

    def custom_process_locale_dir(self, locale_dir, files):
        """
        Extract translatable literals from the specified files, creating or
        updating the POT file for a given locale directory.

        Uses the xgettext GNU gettext utility.
        """
        build_files = []
        for translatable in files:
            if self.verbosity > 1:
                self.stdout.write('processing file %s in %s\n' % (
                    translatable.file, translatable.dirpath
                ))
            if self.domain != 'djangular':
                continue
            build_file = self.build_file_class(self, self.domain, translatable)
            try:
                build_file.preprocess()
            except UnicodeDecodeError as e:
                self.stdout.write(
                    'UnicodeDecodeError: skipped file %s in %s (reason: %s)' % (
                        translatable.file, translatable.dirpath, e,
                    )
                )
                continue
            build_files.append(build_file)

        if self.domain == 'djangular':
            # self.domain = 'django'
            args = [
                'xgettext',
                '-d', self.domain,
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
                '--output=-',
            ]
        else:
            return

        input_files = [bf.work_path for bf in build_files]
        with NamedTemporaryFile(mode='w+') as input_files_list:
            input_files_list.write('\n'.join(input_files))
            input_files_list.flush()
            args.extend(['--files-from', input_files_list.name])
            args.extend(self.xgettext_options)
            msgs, errors, status = popen_wrapper(args)

        if errors:
            if status != STATUS_OK:
                for build_file in build_files:
                    build_file.cleanup()
                raise CommandError(
                    'errors happened while running xgettext on %s\n%s' %
                    ('\n'.join(input_files), errors)
                )
            elif self.verbosity > 0:
                # Print warnings
                self.stdout.write(errors)

        if msgs:
            if locale_dir is NO_LOCALE_DIR:
                file_path = os.path.normpath(build_files[0].path)
                raise CommandError(
                    'Unable to find a locale path to store translations for '
                    'file %s' % file_path
                )
            for build_file in build_files:
                msgs = build_file.postprocess_messages(msgs)
            potfile = os.path.join(locale_dir, '%s.pot' % str(self.domain))
            write_pot_file(potfile, msgs)

        self.domain = 'djangular'

        for build_file in build_files:
            build_file.cleanup()

    def process_locale_dir(self, locale_dir, files):
        if self.is_djangular:
            self.custom_process_locale_dir(locale_dir, files)
        else:
            super().process_locale_dir(locale_dir, files)

    def handle(self, *args, **kwargs):
        self.is_djangular = False
        if kwargs.get('domain') == 'djangular':
            self.is_djangular = True
            kwargs['domain'] = 'django'
            kwargs['extensions'] = ['html']
        super(Command, self).handle(*args, **kwargs)

    def build_potfiles(self):
        # self.domain = 'django'
        if self.is_djangular:
            self.domain = 'djangular'
        return makemessages.Command.build_potfiles(self)
