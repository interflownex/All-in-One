from modules.shared.domain_rules import event_for_create


def test_permissions_create_events_are_business_facing() -> None:
    assert event_for_create("permissions", "user_roles") == "business.role.assigned"
    assert event_for_create("permissions", "access_policies") == "business.user.invited"
