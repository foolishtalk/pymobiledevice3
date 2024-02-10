import json
import logging
from functools import update_wrapper
from pathlib import Path
from urllib.error import URLError

import click

from pymobiledevice3.cli.cli_common import Command, print_json
from pymobiledevice3.cli.ktprint import kt_print
from pymobiledevice3.exceptions import AlreadyMountedError, DeveloperDiskImageNotFoundError, NotMountedError, \
    UnsupportedCommandError, NotFoundImageError
from pymobiledevice3.lockdown import LockdownClient
from pymobiledevice3.lockdown_service_provider import LockdownServiceProvider
from pymobiledevice3.services.mobile_image_mounter import DeveloperDiskImageMounter, MobileImageMounterService, \
    PersonalizedImageMounter, auto_mount

logger = logging.getLogger(__name__)


def catch_errors(func):
    def catch_function(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except AlreadyMountedError:
            logger.error('Given image was already mounted')
        except UnsupportedCommandError:
            logger.error('Your iOS version doesn\'t support this command')

    return update_wrapper(catch_function, func)


@click.group()
def cli():
    """ mounter cli """
    pass


@cli.group()
def mounter():
    """ mounter options """
    pass


# @mounter.command('list', cls=Command)
def mounter_list(service_provider: LockdownClient):
    """ list all mounted images """
    output = []

    images = MobileImageMounterService(lockdown=service_provider).copy_devices()
    for image in images:
        image_signature = image.get('ImageSignature')
        if image_signature is not None:
            image['ImageSignature'] = image_signature.hex()
        output.append(image)

    print_json(output)


# @mounter.command('lookup', cls=Command)
# @click.argument('image_type')
def mounter_lookup(service_provider: LockdownClient, image_type):
    """ lookup mounter image type """
    try:
        signature = MobileImageMounterService(lockdown=service_provider).lookup_image(image_type)
        print_json(signature)
    except NotMountedError:
        logger.error(f'Disk image of type: {image_type} is not mounted')


# @mounter.command('umount-developer', cls=Command)
# @catch_errors
def mounter_umount_developer(service_provider: LockdownClient):
    """ unmount Developer image """
    try:
        DeveloperDiskImageMounter(lockdown=service_provider).umount()
        logger.info('Developer image unmounted successfully')
    except NotMountedError:
        logger.error('Developer image isn\'t currently mounted')


# @mounter.command('umount-personalized', cls=Command)
# @catch_errors
def mounter_umount_personalized(service_provider: LockdownClient):
    """ unmount Personalized image """
    try:
        PersonalizedImageMounter(lockdown=service_provider).umount()
        logger.info('Personalized image unmounted successfully')
    except NotMountedError:
        logger.error('Personalized image isn\'t currently mounted')


# @mounter.command('mount-developer', cls=Command)
# @click.argument('image', type=click.Path(exists=True, file_okay=True, dir_okay=False))
# @click.argument('signature', type=click.Path(exists=True, file_okay=True, dir_okay=False))
# @catch_errors
def mounter_mount_developer(service_provider: LockdownClient, image: str, signature: str):
    """ mount developer image """
    DeveloperDiskImageMounter(lockdown=service_provider).mount(Path(image), Path(signature))
    logger.info('Developer image mounted successfully')


# @mounter.command('mount-personalized', cls=Command)
# @click.argument('image', type=click.Path(exists=True, file_okay=True, dir_okay=False))
# @click.argument('trust-cache', type=click.Path(exists=True, file_okay=True, dir_okay=False))
# @click.argument('build-manifest', type=click.Path(exists=True, file_okay=True, dir_okay=False))
# @catch_errors
def mounter_mount_personalized(service_provider: LockdownClient, image: str, trust_cache: str, build_manifest: str):
    """ mount personalized image """
    PersonalizedImageMounter(lockdown=service_provider).mount(Path(image), Path(build_manifest), Path(trust_cache))
    logger.info('Personalized image mounted successfully')


@mounter.command('auto-mount', cls=Command)
@click.option('--path', help='the iOS 17 DeveloperDiskImage path')
@click.option('-x', '--xcode', type=click.Path(exists=True, dir_okay=True, file_okay=False),
              help='Xcode application path used to figure out automatically the DeveloperDiskImage path')
@click.option('-v', '--version', help='use a different DeveloperDiskImage version from the one retrieved by lockdown'
                                      'connection')
def mounter_auto_mount(service_provider: LockdownServiceProvider, path: str, xcode: str, version: str):
    """ auto-detect correct DeveloperDiskImage and mount it """
    try:
        auto_mount(service_provider, path=path, xcode=xcode, version=version)
        data = {'cmd': 'mounter_auto_mount',
                'UDID': f'{service_provider.udid}',
                'code': 0,
                'msg': 'DeveloperDiskImage mounted successfully',
                }
        json_str = json.dumps(data)
        kt_print(json_str)
    except URLError:
        data = {'cmd': 'mounter_auto_mount',
                'UDID': f'{service_provider.udid}',
                'code': 1,
                'msg': 'failed to query DeveloperDiskImage versions',
                }
        json_str = json.dumps(data)
        kt_print(json_str)
    except DeveloperDiskImageNotFoundError:
        data = {'cmd': 'mounter_auto_mount',
                'UDID': f'{service_provider.udid}',
                'code': 2,
                'msg': 'Unable to find the correct DeveloperDiskImage',
                }
        json_str = json.dumps(data)
        kt_print(json_str)
    except AlreadyMountedError:
        data = {'cmd': 'mounter_auto_mount',
                'UDID': f'{service_provider.udid}',
                'code': 3,
                'msg': 'DeveloperDiskImage already mounted',
                }
        json_str = json.dumps(data)
        kt_print(json_str)
    except NotFoundImageError:
        data = {'cmd': 'mounter_auto_mount',
                'UDID': f'{service_provider.udid}',
                'code': 4,
                'msg': 'DeveloperDiskImage not found',
                }
        json_str = json.dumps(data)
        kt_print(json_str)
    except PermissionError as e:
        data = {'cmd': 'mounter_auto_mount',
                'UDID': f'{service_provider.udid}',
                'code': 5,
                'msg': f'DeveloperDiskImage could not be saved to Xcode default path ({e.filename}).Please make sure your user has the necessary permissions',
                }
        json_str = json.dumps(data)
        kt_print(json_str)


# @mounter.command('query-developer-mode-status', cls=Command)
def mounter_query_developer_mode_status(service_provider: LockdownClient):
    """ Query developer mode status """
    print_json(MobileImageMounterService(lockdown=service_provider).query_developer_mode_status())


# @mounter.command('query-nonce', cls=Command)
# @click.option('--image-type')
def mounter_query_nonce(service_provider: LockdownClient, image_type: str):
    """ Query nonce """
    print_json(MobileImageMounterService(lockdown=service_provider).query_nonce(image_type))


# @mounter.command('query-personalization-identifiers', cls=Command)
def mounter_query_personalization_identifiers(service_provider: LockdownClient):
    """ Query personalization identifiers """
    print_json(MobileImageMounterService(lockdown=service_provider).query_personalization_identifiers())


# @mounter.command('query-personalization-manifest', cls=Command)
def mounter_query_personalization_manifest(service_provider: LockdownClient):
    """ Query personalization manifest """
    result = []
    mounter = MobileImageMounterService(lockdown=service_provider)
    for device in mounter.copy_devices():
        result.append(mounter.query_personalization_manifest(device['PersonalizedImageType'], device['ImageSignature']))
    print_json(result)


# @mounter.command('roll-personalization-nonce', cls=Command)
def mounter_roll_personalization_nonce(service_provider: LockdownClient):
    MobileImageMounterService(lockdown=service_provider).roll_personalization_nonce()


# @mounter.command('roll-cryptex-nonce', cls=Command)
def mounter_roll_cryptex_nonce(service_provider: LockdownClient):
    """ Roll cryptex nonce (will reboot) """
    MobileImageMounterService(lockdown=service_provider).roll_cryptex_nonce()
