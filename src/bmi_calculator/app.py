"""以主控台互動方式計算 BMI，並顯示對應的體重分類。"""


def _get_measurements():
    """依序讀取使用者的體重與身高。

    Returns:
        tuple[float, float]: 體重（公斤）與身高（英吋）。
    """
    weight = float(input("Enter your weight in kg: "))
    height_in_inches = float(input("Enter your height in inches: "))
    return weight, height_in_inches


def _calculate_bmi(weight, height_in_inches):
    """將身高由英吋換算為公尺，並計算 BMI。

    Args:
        weight: 使用者體重，單位為公斤。
        height_in_inches: 使用者身高，單位為英吋。

    Returns:
        float: 依體重除以身高平方計算出的 BMI 值。
    """
    height_in_meters = height_in_inches * 0.0254
    return weight / (height_in_meters ** 2)


def _classify_bmi(bmi):
    """依 BMI 門檻回傳體重分類。

    分類區間依序為低於 18.5、18.5 至低於 24、24 至低於 27，
    以及 27 以上；等於門檻時會歸入下一個分類。

    Args:
        bmi: 已計算完成的 BMI 值。

    Returns:
        str: Underweight、Normal weight、Overweight 或 Obesity。
    """
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 24:
        return "Normal weight"
    elif bmi < 27:
        return "Overweight"
    return "Obesity"


def _display_result(bmi, category):
    """以固定格式顯示 BMI 與其分類。

    BMI 顯示至小數點後兩位；分類文字依呼叫端傳入的結果呈現。
    """
    print(f"Your BMI is {bmi:.2f}. You are classified as {category}.")


def bmi_calculator():
    """協調輸入、BMI 計算、分類與結果顯示的主流程。"""
    weight, height_in_inches = _get_measurements()
    bmi = _calculate_bmi(weight, height_in_inches)
    category = _classify_bmi(bmi)
    _display_result(bmi, category)


# 只有直接執行此檔案時才啟動主控台互動；匯入模組時不會自動讀取輸入。
if __name__ == "__main__":
    bmi_calculator()