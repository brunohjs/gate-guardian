import pytest
from src.PIIDetector import PIIDetector
from src.Entity import Entity


pii = PIIDetector()


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        (
            "Esse é meu email teste@teste.com",
            [Entity(name="EMAIL_ADDRESS", value="teste@teste.com", start=17, end=32)],
        ),
        (
            "outro.teste@seila.com.br",
            [Entity(name="EMAIL_ADDRESS", value="outro.teste@seila.com.br", start=0, end=24)],
        ),
        (
            "iawhdqprhqwoieafa opa@aaaaa.net.op qwuihquiwehqiwhe1i2heiouhqiw",
            [Entity(name="EMAIL_ADDRESS", value="opa@aaaaa.net.op", start=18, end=34)],
        ),
        (
            "esse é um email invalido: emailinvalido@a. Ok?",
            [],
        ),
        (
            "esse é um email válido: email@valido.com.uk. Ok?",
            [Entity(name='EMAIL_ADDRESS', value='email@valido.com.uk', start=24, end=43)],
        ),
        (
            "esse é outro email invalido: email?@invalido.com.uk. Ok?",
            [],
        )
    ],
)
def test_email_checker(text, expected):
    assert pii.email_checker(text) == expected
