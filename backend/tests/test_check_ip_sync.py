import backend.application.use_cases.check_ip_sync as module
from backend.application.use_cases.check_ip_sync import CheckIPSyncUseCase


def test_execute_ip_unchanged(mocker):

    # --------------------
    # MOCK DEPENDENCIES
    # --------------------
    mocker.patch.object(module, "get_public_ip", return_value="1.1.1.1")
    mocker.patch.object(module, "get_current_ip_status", return_value={
        "current_ip": "1.1.1.1"
    })

    mocker.patch.object(module, "get_records", return_value=[])
    mocker.patch.object(module, "get_providers", return_value=[])
    mocker.patch.object(module, "emit_event")

    # --------------------
    # EXECUTE
    # --------------------
    use_case = CheckIPSyncUseCase(providers_cache={})
    result = use_case.execute()

    # --------------------
    # ASSERT
    # --------------------
    assert result == "1.1.1.1"
    module.emit_event.assert_not_called()

def test_execute_ip_changed(mocker):

    import backend.application.use_cases.check_ip_sync as module

    mocker.patch.object(module, "get_public_ip", return_value="2.2.2.2")
    mocker.patch.object(module, "get_current_ip_status", return_value={
        "current_ip": "1.1.1.1"
    })

    mocker.patch.object(module, "add_ip_history")
    mocker.patch.object(module, "get_records", return_value=[])
    mocker.patch.object(module, "get_providers", return_value=[])
    mocker.patch.object(module, "emit_event")

    use_case = CheckIPSyncUseCase(providers_cache={})
    result = use_case.execute()

    module.add_ip_history.assert_called_once()
    module.emit_event.assert_any_call(
        "IP_CHANGED",
        {
            "old_ip": "1.1.1.1",
            "new_ip": "2.2.2.2"
        },
        domain="system"
    )