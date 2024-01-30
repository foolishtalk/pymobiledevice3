import logging
import sys
import traceback
import json
import click
from pymobiledevice3.cli.ktprint import kt_print
#  自己加的引用 start
from Crypto.Cipher import AES
from binascii import a2b_hex
# 自己加的引用 end

from pymobiledevice3.exceptions import AccessDeniedError, ConnectionFailedToUsbmuxdError, DeprecationError, \
    DeveloperModeError, DeveloperModeIsNotEnabledError, DeviceHasPasscodeSetError, DeviceNotFoundError, InternalError, \
    InvalidServiceError, MessageNotSupportedError, MissingValueError, NoDeviceConnectedError, NoDeviceSelectedError, \
    NotEnoughDiskSpaceError, NotPairedError, PairingDialogResponsePendingError, PasswordRequiredError, \
    RSDRequiredError, SetProhibitedError, TunneldConnectionError, UserDeniedPairingError

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

INVALID_SERVICE_MESSAGE = """Failed to start service. Possible reasons are:
- If you were trying to access a developer service (developer subcommand):
    - Make sure the DeveloperDiskImage/PersonalizedImage is mounted via:
      > python3 -m pymobiledevice3 mounter auto-mount

    - If your device iOS version >= 17.0:
        - Make sure you passed the --rsd option to the subcommand
          https://github.com/doronz88/pymobiledevice3#working-with-developer-tools-ios--170

- Apple removed this service

- A bug. Please file a bug report:
  https://github.com/doronz88/pymobiledevice3/issues/new?assignees=&labels=&projects=&template=bug_report.md&title=
"""

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

# Mapping of index options to import file names
CLI_GROUPS = {
    'activation': 'activation',
    'afc': 'afc',
    'amfi': 'amfi',
    'apps': 'apps',
    'backup2': 'backup',
    'bonjour': 'bonjour',
    'companion': 'companion_proxy',
    'crash': 'crash',
    'developer': 'developer',
    'diagnostics': 'diagnostics',
    'lockdown': 'lockdown',
    'mounter': 'mounter',
    'notification': 'notification',
    'pcap': 'pcap',
    'power-assertion': 'power_assertion',
    'processes': 'processes',
    'profile': 'profile',
    'provision': 'provision',
    'remote': 'remote',
    'restore': 'restore',
    'springboard': 'springboard',
    'syslog': 'syslog',
    'usbmux': 'usbmux',
    'webinspector': 'webinspector',
    'version': 'version',
}


class Pmd3Cli(click.Group):
    def list_commands(self, ctx):
        return CLI_GROUPS.keys()

    def get_command(self, ctx, name):
        if name not in CLI_GROUPS.keys():
            ctx.fail(f'No such command {name!r}.')
        mod = __import__(f'pymobiledevice3.cli.{CLI_GROUPS[name]}', None, None, ['cli'])
        command = mod.cli.get_command(ctx, name)
        # Some cli groups have different names than the index
        if not command:
            command_name = mod.cli.list_commands(ctx)[0]
            command = mod.cli.get_command(ctx, command_name)
        return command


@click.command(cls=Pmd3Cli, context_settings=CONTEXT_SETTINGS)
def cli():
    pass


def main() -> None:
    password_result = False
    password_verify_result = False
    index = 0
    for argv in sys.argv:
        if argv == "--password":
            password_result = True
        if argv == "password_verify":
            password_verify_result = True
        if argv == "--verify":
            str = decrypt(sys.argv[2])
            args = str.split(" ")
            # 加密后可能会出现\x01
            for i in range(len(args)):
                char = ""
                for every_char in iter(args[i]):
                    if every_char.isdigit():
                        char = char + every_char
                    elif every_char.isalpha():
                        char = char + every_char
                    elif every_char == ",":
                        char = char + ","
                    elif every_char == ".":
                        char = char + "."
                    elif every_char == "-":
                        char = char + "-"
                    elif every_char == "_":
                        char = char + "_"
                    else:
                        break
                args[i] = char
            args.insert(0, sys.argv[0])
            sys.argv = args
            main()
            return
        index += 1
    if (password_result is False) or (password_verify_result is False):
        return
    sys.argv.remove("password_verify")
    sys.argv.remove("--password")
    try:
        cli()
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
    except ConnectionFailedToUsbmuxdError:
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
        data = {'cmd': 'mounter_auto_mount',
                'code': 6,
                'msg': 'Failed to start service',
                }
        json_str = json.dumps(data)
        kt_print(json_str)
        # logger.error(INVALID_SERVICE_MESSAGE)
    except NoDeviceSelectedError:
        return
    except PasswordRequiredError:
        logger.error('Device is password protected. Please unlock and retry')
    except AccessDeniedError:
        if sys.platform == 'win32':
            logger.error('This command requires admin privileges. Consider retrying with "run-as administrator".')
        else:
            logger.error('This command requires root privileges. Consider retrying with "sudo".')
    except BrokenPipeError:
        traceback.print_exc()
    except TunneldConnectionError:
        logger.error(
            'Unable to connect to Tunneld. You can start one using:\n'
            'sudo python3 -m pymobiledevice3 remote tunneld')
    except DeviceNotFoundError as e:
        logger.error(f'Device not found: {e.udid}')
    except NotEnoughDiskSpaceError:
        logger.error('Not enough disk space')
    except RSDRequiredError:
        logger.error('The requested operation requires an RSD instance. For more information see:\n'
                     'https://github.com/doronz88/pymobiledevice3?tab=readme-ov-file#working-with-developer-tools-ios--170')
    except DeprecationError:
        logger.error('failed to query MobileGestalt, MobileGestalt deprecated (iOS >= 17.4).')


def decrypt(plaintext):
    # 定义密钥
    key = 'pydevice_key_psw'.encode('utf-8')
    # 定义 IV
    iv = b'pydevie373805110'
    # 创建 AES 对象
    cipher = AES.new(key, AES.MODE_CBC, iv)
    hex = a2b_hex(plaintext)
    # 解密
    hex = cipher.decrypt(hex)
    decrypt_str = bytes.decode(hex).rstrip('\0')
    # 打印明文
    return decrypt_str


if __name__ == '__main__':
    main()
