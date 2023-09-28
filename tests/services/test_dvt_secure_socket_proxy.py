from pathlib import Path

import pytest

from pymobiledevice3.exceptions import AlreadyMountedError, DvtDirListError, UnrecognizedSelectorError
from pymobiledevice3.lockdown import create_using_usbmux
from pymobiledevice3.services.dvt.dvt_secure_socket_proxy import DvtSecureSocketProxyService
from pymobiledevice3.services.dvt.instruments.application_listing import ApplicationListing
from pymobiledevice3.services.dvt.instruments.device_info import DeviceInfo
from pymobiledevice3.services.dvt.instruments.process_control import ProcessControl
from pymobiledevice3.services.mobile_image_mounter import DeveloperDiskImageMounter

DEVICE_SUPPORT = Path('/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform/DeviceSupport')
IMAGE_TYPE = 'Developer'


@pytest.fixture(scope='module', autouse=True)
def mount_developer_disk_image():
    with create_using_usbmux() as lockdown:
        with DeveloperDiskImageMounter(lockdown=lockdown) as mounter:
            if mounter.is_image_mounted('Developer'):
                yield
            image_path = DEVICE_SUPPORT / mounter.lockdown.product_version / 'DeveloperDiskImage.dmg'
            try:
                mounter.mount(image_path, image_path.with_suffix('.dmg.signature'))
            except AlreadyMountedError:
                pass


def get_process_data(lockdown, name):
    with DvtSecureSocketProxyService(lockdown=lockdown) as dvt:
        processes = DeviceInfo(dvt).proclist()
    return [process for process in processes if process['name'] == name][0]


def test_ls(lockdown):
    """
    Test listing a directory.
    :param pymobiledevice3.lockdown.LockdownClient lockdown: Lockdown client.
    """
    with DvtSecureSocketProxyService(lockdown=lockdown) as dvt:
        ls = set(DeviceInfo(dvt).ls('/'))
    assert {'usr', 'bin', 'etc', 'var', 'private', 'Applications', 'Developer'} <= ls


def test_ls_failure(lockdown):
    """
    Test listing a directory.
    :param pymobiledevice3.lockdown.LockdownClient lockdown: Lockdown client.
    """
    with DvtSecureSocketProxyService(lockdown=lockdown) as dvt:
        with pytest.raises(DvtDirListError):
            DeviceInfo(dvt).ls('Directory that does not exist')


def test_proclist(lockdown):
    """
    Test listing processes.
    :param pymobiledevice3.lockdown.LockdownClient lockdown: Lockdown client.
    """
    lockdownd = get_process_data(lockdown, 'lockdownd')
    assert lockdownd['realAppName'] == '/usr/libexec/lockdownd'
    assert not lockdownd['isApplication']


def test_applist(lockdown):
    """
    Test listing applications.
    :param pymobiledevice3.lockdown.LockdownClient lockdown: Lockdown client.
    """
    with DvtSecureSocketProxyService(lockdown=lockdown) as dvt:
        apps = ApplicationListing(dvt).applist()

    safari = [app for app in apps if app['DisplayName'] == 'StocksWidget'][0]
    assert safari['CFBundleIdentifier'] == 'com.apple.stocks.widget'
    assert safari['Restricted'] == 1
    assert safari['Type'] == 'PluginKit'


def test_kill(lockdown):
    """
    Test killing a process.
    :param pymobiledevice3.lockdown.LockdownClient lockdown: Lockdown client.
    """
    aggregated = get_process_data(lockdown, 'aggregated')

    with DvtSecureSocketProxyService(lockdown=lockdown) as dvt:
        ProcessControl(dvt).kill(aggregated['pid'])

    aggregated_after_kill = get_process_data(lockdown, 'aggregated')
    if 'startDate' in aggregated:
        assert aggregated['startDate'] < aggregated_after_kill['startDate']


def test_launch(lockdown):
    """
    Test launching a process.
    :param pymobiledevice3.lockdown.LockdownClient lockdown: Lockdown client.
    """
    with DvtSecureSocketProxyService(lockdown=lockdown) as dvt:
        pid = ProcessControl(dvt).launch('com.apple.mobilesafari')
        assert pid
    with DvtSecureSocketProxyService(lockdown=lockdown) as dvt:
        for process in DeviceInfo(dvt).proclist():
            if pid == process['pid']:
                assert process['name'] == 'MobileSafari'


def test_system_information(lockdown):
    """
    Test getting system information.
    :param pymobiledevice3.lockdown.LockdownClient lockdown: Lockdown client.
    """
    try:
        with DvtSecureSocketProxyService(lockdown=lockdown) as dvt:
            system_info = DeviceInfo(dvt).system_information()
    except UnrecognizedSelectorError:
        pytest.skip('device doesn\'t support this method')
    assert '_deviceDescription' in system_info and system_info['_deviceDescription'].startswith('Build Version')


def test_hardware_information(lockdown):
    """
    Test getting hardware information.
    :param pymobiledevice3.lockdown.LockdownClient lockdown: Lockdown client.
    """
    with DvtSecureSocketProxyService(lockdown=lockdown) as dvt:
        hardware_info = DeviceInfo(dvt).hardware_information()
    assert hardware_info['numberOfCpus'] > 0


def test_network_information(lockdown):
    """
    Test getting network information.
    :param pymobiledevice3.lockdown.LockdownClient lockdown: Lockdown client.
    """
    with DvtSecureSocketProxyService(lockdown=lockdown) as dvt:
        network_info = DeviceInfo(dvt).network_information()
    assert network_info['lo0'] == 'Loopback'
