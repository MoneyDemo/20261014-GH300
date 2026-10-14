"""BMI 分類門檻的單元測試，每個情境都是獨立函式。"""

from assertpy import assert_that

from bmi_calculator.app import _classify_bmi


def test_classify_bmi_below_18_5_as_underweight():
    """低於 18.5 時應分類為體重過輕。"""
    # Arrange：準備低於第一個門檻的 BMI。
    bmi = 18.49
    expected_category = "Underweight"

    # Act：取得分類。
    actual_category = _classify_bmi(bmi)

    # Assert：驗證分類與預期一致。
    assert_that(actual_category).is_equal_to(expected_category)


def test_classify_bmi_at_18_5_as_normal_weight():
    """等於 18.5 時應歸入正常體重。"""
    # Arrange：準備正常體重的下界。
    bmi = 18.5
    expected_category = "Normal weight"

    # Act：取得分類。
    actual_category = _classify_bmi(bmi)

    # Assert：驗證分類包含下界。
    assert_that(actual_category).is_equal_to(expected_category)


def test_classify_bmi_below_24_as_normal_weight():
    """低於 24 且不低於 18.5 時應分類為正常體重。"""
    # Arrange：準備接近正常體重上界的 BMI。
    bmi = 23.99
    expected_category = "Normal weight"

    # Act：取得分類。
    actual_category = _classify_bmi(bmi)

    # Assert：驗證尚未跨過門檻。
    assert_that(actual_category).is_equal_to(expected_category)


def test_classify_bmi_at_24_as_overweight():
    """等於 24 時應歸入過重。"""
    # Arrange：準備過重的下界。
    bmi = 24
    expected_category = "Overweight"

    # Act：取得分類。
    actual_category = _classify_bmi(bmi)

    # Assert：驗證分類包含下界。
    assert_that(actual_category).is_equal_to(expected_category)


def test_classify_bmi_below_27_as_overweight():
    """低於 27 且不低於 24 時應分類為過重。"""
    # Arrange：準備接近過重上界的 BMI。
    bmi = 26.99
    expected_category = "Overweight"

    # Act：取得分類。
    actual_category = _classify_bmi(bmi)

    # Assert：驗證尚未跨過門檻。
    assert_that(actual_category).is_equal_to(expected_category)


def test_classify_bmi_at_27_as_obesity():
    """等於 27 時應歸入肥胖。"""
    # Arrange：準備肥胖的下界。
    bmi = 27
    expected_category = "Obesity"

    # Act：取得分類。
    actual_category = _classify_bmi(bmi)

    # Assert：驗證分類包含下界。
    assert_that(actual_category).is_equal_to(expected_category)