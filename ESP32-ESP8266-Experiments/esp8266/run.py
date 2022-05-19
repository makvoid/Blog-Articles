from machine_sensor import MachineSensor

# Use dry_run to flip between testing/live
ms = MachineSensor(dry_run=True)
ms.run()
