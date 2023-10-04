#!/usr/bin/env python3
import logging
import sys
import traceback

import click

from pymobiledevice3.cli.activation import cli as activation_cli
from pymobiledevice3.cli.afc import cli as afc_cli
from pymobiledevice3.cli.amfi import cli as amfi_cli
from pymobiledevice3.cli.apps import cli as apps_cli
from pymobiledevice3.cli.backup import cli as backup_cli
from pymobiledevice3.cli.companion_proxy import cli as companion_cli
from pymobiledevice3.cli.developer import cli as developer_cli
from pymobiledevice3.cli.lockdown import cli as lockdown_cli
from pymobiledevice3.cli.mounter import cli as mounter_cli
from pymobiledevice3.cli.pcap import cli as pcap_cli
from pymobiledevice3.cli.power_assertion import cli as power_assertion_cli
from pymobiledevice3.cli.profile import cli as profile_cli
from pymobiledevice3.cli.provision import cli as provision_cli
from pymobiledevice3.cli.remote import cli as remote_cli
from pymobiledevice3.cli.syslog import cli as syslog_cli
from pymobiledevice3.cli.usbmux import cli as usbmux_cli
from pymobiledevice3.exceptions import AccessDeniedError, ConnectionFailedError, DeveloperModeError, \
    DeveloperModeIsNotEnabledError, DeviceHasPasscodeSetError, InternalError, InvalidServiceError, \
    MessageNotSupportedError, MissingValueError, NoDeviceConnectedError, NoDeviceSelectedError, NotPairedError, \
    PairingDialogResponsePendingError, PasswordRequiredError, SetProhibitedError, UserDeniedPairingError


logging.getLogger('quic').disabled = True
logging.getLogger('asyncio').disabled = True
logging.getLogger('zeroconf').disabled = True
logging.getLogger('parso.cache').disabled = True
logging.getLogger('parso.cache.pickle').disabled = True
logging.getLogger('parso.python.diff').disabled = True
logging.getLogger('humanfriendly.prompts').disabled = True
logging.getLogger('blib2to3.pgen2.driver').disabled = True
logging.getLogger('urllib3.connectionpool').disabled = True

logger = logging.getLogger(__name__)


def cli():
    password_result = False
    password_verify_result = False
    password_index = 0
    password_verify_index = 0
    index = 0
    for argv in sys.argv:
        if argv == "--password":
            password_result = True
            password_index = index
        if argv == "password_verify":
            password_verify_result = True
            password_index = index
        index += 1
    if password_index == 0 and password_verify_index == 0:
        return
    sys.argv.pop(password_index)
    sys.argv.pop(password_verify_index)

    cli_commands = click.CommandCollection(sources=[
        developer_cli, mounter_cli, apps_cli, profile_cli, lockdown_cli, syslog_cli, pcap_cli,
        usbmux_cli, power_assertion_cli,
        provision_cli, backup_cli, activation_cli, companion_cli, amfi_cli,
        remote_cli
    ])
    cli_commands.context_settings = dict(help_option_names=['-h', '--help'])
    try:
        cli_commands()
    except NoDeviceConnectedError:
        logger.error('Device is not connected')
    except ConnectionAbortedError:
        logger.error('Device was disconnected')
    except NotPairedError:
        logger.error('Device is not paired')
    except UserDeniedPairingError:
        logger.error('User refused to trust this computer')
    except PairingDialogResponsePendingError:
        logger.error('Waiting for user dialog approval')
    except SetProhibitedError:
        logger.error('lockdownd denied the access')
    except MissingValueError:
        logger.error('No such value')
    except DeviceHasPasscodeSetError:
        logger.error('Cannot enable developer-mode when passcode is set')
    except DeveloperModeError as e:
        logger.error(f'Failed to enable developer-mode. Error: {e}')
    except ConnectionFailedError:
        logger.error('Failed to connect to usbmuxd socket. Make sure it\'s running.')
    except MessageNotSupportedError:
        logger.error('Message not supported for this iOS version')
        traceback.print_exc()
    except InternalError:
        logger.error('Internal Error')
    except DeveloperModeIsNotEnabledError:
        logger.error('Developer Mode is disabled. You can try to enable it using: '
                     'python3 -m pymobiledevice3 amfi enable-developer-mode')
    except InvalidServiceError:
        logger.error('Failed to access an invalid lockdown service, possibly from DeveloperDiskImage.dmg or a Cryptex. '
                     'You may try: python3 -m pymobiledevice3 mounter auto-mount')
    except NoDeviceSelectedError:
        return
    except PasswordRequiredError:
        logger.error('Device is password protected. Please unlock and retry')
    except AccessDeniedError:
        logger.error('This command requires root privileges. Consider retrying with "sudo".')
    except BrokenPipeError:
        traceback.print_exc()


if __name__ == '__main__':
    temp = sys.stdout
    sys.stderr = temp
    cli()
