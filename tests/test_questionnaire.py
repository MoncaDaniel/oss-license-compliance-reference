"""Tests for the business-context questionnaire, using injected input/print
so no real stdin/stdout is needed."""

from oss_compliance.questionnaire import ProductQuestionnaire


def make_questionnaire(answers):
    it = iter(answers)
    return ProductQuestionnaire(input_fn=lambda _prompt: next(it), print_fn=lambda *_a, **_k: None)


def test_capture_product_context_correctly():
    answers = [
        "Signaling Platform",  # product name
        "2",  # use case -> Embedded
        "3",  # data types -> Industrial/operational data
        "EU, UK",  # target markets
        "yes",  # safety critical
        "yes",  # has AI
        "no",  # modifications expected
    ]
    q = make_questionnaire(answers)
    context = q.ask_user()

    assert context.product_name == "Signaling Platform"
    assert context.use_case == "Embedded"
    assert context.data_types == ["Industrial/operational data"]
    assert context.target_markets == ["EU", "UK"]
    assert context.is_safety_critical is True
    assert context.has_ai is True
    assert context.modifications_expected is False


def test_validate_use_case_options_out_of_range_falls_back_to_default():
    answers = ["Product", "99", "1", "", "no", "no", "no"]
    q = make_questionnaire(answers)
    context = q.ask_user()
    assert context.use_case == "Internal"


def test_data_types_both_option_expands_to_two_entries():
    answers = ["Product", "1", "4", "", "no", "no", "no"]
    q = make_questionnaire(answers)
    context = q.ask_user()
    assert context.data_types == ["Customer data (GDPR-protected)", "Industrial/operational data"]


def test_parse_target_markets_from_comma_separated_input():
    answers = ["Product", "1", "1", "EU, US, Asia", "no", "no", "no"]
    q = make_questionnaire(answers)
    context = q.ask_user()
    assert context.target_markets == ["EU", "US", "Asia"]


def test_yes_no_questions_handle_variants():
    q = make_questionnaire(["Y"])
    assert q._ask_yes_no("Safety critical?") is True
    q2 = make_questionnaire(["nah"])
    assert q2._ask_yes_no("Safety critical?") is False


def test_returns_product_context_object():
    from oss_compliance.models import ProductContext

    answers = ["Product", "1", "1", "", "no", "no", "no"]
    q = make_questionnaire(answers)
    context = q.ask_user()
    assert isinstance(context, ProductContext)
