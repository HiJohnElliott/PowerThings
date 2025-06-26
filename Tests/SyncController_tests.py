import SyncController as Sync


def test_parse_duration_tag() -> None: 
    assert Sync.parse_duration_tag('15m') == 15
    assert Sync.parse_duration_tag('1h') == 60
    assert Sync.parse_duration_tag('3h') == 180
    assert Sync.parse_duration_tag('3d') == 60



if __name__ == "__main__":
    print(test_parse_duration_tag())
