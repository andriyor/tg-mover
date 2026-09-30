import re

from tg_mover.cli import matches

# same regex as in .env.example
social = re.compile(r"(?<![\w.-])(?:https?://)?(?:www\.|mobile\.|m\.)?(?:x|twitter|instagram)\.com/", re.I)

assert matches("look https://x.com/user/status/1", social)
assert matches("x.com/user", social)
assert matches("https://twitter.com/user", social)
assert matches("https://www.instagram.com/p/abc/", social)
assert matches("[post](https://X.com/a)", social)  # hidden link, markdown form
assert not matches("https://fox.com/news", social)
assert not matches("https://youtube.com/watch?v=1", social)
assert not matches("just text", social)
assert not matches(None, social)

# no filter -> everything matches
assert matches("anything", None)
assert matches(None, None)
print("ok")
