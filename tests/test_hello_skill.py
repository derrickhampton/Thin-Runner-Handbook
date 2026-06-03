from skills.hello_world.run import run


def test_hello_world_skill_returns_structured_output() -> None:
    result = run({"name": "Thin Runner"})
    assert result["message"] == "Hello, Thin Runner!"
    assert result["skill"] == "hello_world"
    assert result["status"] == "success"


def test_hello_world_defaults_name_when_missing() -> None:
    result = run({})
    assert result["message"] == "Hello, Thin Runner!"


def test_hello_world_normalizes_blank_name() -> None:
    result = run({"name": "   "})
    assert result["message"] == "Hello, Thin Runner!"
