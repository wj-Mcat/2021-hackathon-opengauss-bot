from advertools import extract_emoji

def test_emoji_extraction():
    a = ['sdfs😓ssf', '👻😓']
    emojis = extract_emoji(a)
    assert len(emojis['emoji']) == 2