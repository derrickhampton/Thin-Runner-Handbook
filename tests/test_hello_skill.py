from skills.hello_world.run import run


def test_hello_world_skill_returns_message() -> None:
    result = run({"name": "Tester"})
    assert result["message"] == "Hello, Tester!"
