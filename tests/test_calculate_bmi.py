"""BMI 計算的單元測試。"""

from assertpy import assert_that

from bmi_calculator.app import _calculate_bmi


def test_calculate_bmi_converts_height_from_inches_to_meters():
    """驗證公斤與英吋輸入可計算出已知的 BMI。"""
    # Arrange：準備體重、身高與預期結果。
    weight = 57
    height_in_inches = 67
    expected_bmi = 19.68

    # Act：直接呼叫計算函式，不經過主控台輸入。
    actual_bmi = _calculate_bmi(weight, height_in_inches)

    # Assert：以 Fluent Assertion 比較小數點後兩位的結果。
    assert_that(round(actual_bmi, 2)).is_equal_to(expected_bmi)