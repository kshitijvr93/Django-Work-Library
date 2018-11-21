from cloudstorage.drivers.local import LocalDriver

driver_cls = get_driver_by_name('LOCAL')
storage = driver_cls(key='/c/rvp/storage', secret='<my-secret>')
