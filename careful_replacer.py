import os
import os.path
import shutil
import logging
import tempfile

LOGGER = logging.getLogger(__name__)

def replace_careful(source, target):
    '''Replace a binary while a process is using it (it's running)

    :param source: Replacement binary path
    :type source: str
    :param target: Target path
    :type target: str
    '''

    LOGGER.info('Replacing %s with %s', target, source)

    target_abs = os.path.abspath(target)
    LOGGER.debug('Resolved target as %s', target_abs)
    source_abs = os.path.abspath(source)
    LOGGER.debug('Resolved source as %s', source_abs)

    if not os.path.isfile(source):
        raise ValueError('Source is not a valid file')

    target_dirname = os.path.dirname(target_abs)
    if not os.path.isdir(target_dirname):
        raise ValueError('Target folder doen\'t exist')

    target_basename = os.path.basename(target_abs)

    # Move target out of the way
    target_backup_copy = None

    if os.path.exists(target_abs):
        LOGGER.info('Target exists')

        LOGGER.debug('Creating backup copy of target')
        (fd, target_backup_copy) = tempfile.mkstemp(prefix=target_basename,
            dir=target_dirname)
        # Unlinking the file here is dangerous, normally, since another thread
        # of execution could create the same tempfile in between. Here there's
        # no issue since we use rename later on
        try:
            os.unlink(target_backup_copy)
        finally:
            os.close(fd)

        os.rename(target_abs, target_backup_copy)

        LOGGER.debug('Backup copy at %s', target_backup_copy)

    else:
        LOGGER.info('Target doesn\'t exist')

    # Now target is out of the way. Try to put source in place
    try:
        # Check whether source is on same FS as target
        source_stat = os.stat(source_abs)
        target_dir_stat = os.stat(target_dirname)

        if source_stat.st_dev == target_dir_stat.st_dev:
            LOGGER.debug('Source on target FS, create hardlink')

            os.link(source_abs, target_abs)
        else:
            LOGGER.debug('Source not on target FS, using copy & link')

            (fd, temp_copy) = tempfile.mkstemp(prefix=target_basename,
                dir=target_dirname)
            LOGGER.debug('Copying source to %s', temp_copy)
            try:
                shutil.copyfile(source_abs, temp_copy)
            finally:
                os.close(fd)

            os.rename(temp_copy, target_abs)

        LOGGER.debug('Copying stat info from source')
        shutil.copystat(source_abs, target_abs)

    except:
        LOGGER.exception('Exception during replace, rolling back')

        if target_backup_copy is not None:
            if os.path.isfile(target_abs):
                os.unlink(target_abs)

            LOGGER.debug('Relinking backup copy %s', target_backup_copy)
            os.rename(target_backup_copy, target_abs)

        raise
    else:
        if target_backup_copy is not None:
            LOGGER.debug('Removing target backup copy %s', target_backup_copy)
            os.unlink(target_backup_copy)

if __name__ == '__main__':
    import sys

    logging.basicConfig(level=logging.DEBUG)

    src, dest = sys.argv[1:3]
    replace_careful(src, dest)