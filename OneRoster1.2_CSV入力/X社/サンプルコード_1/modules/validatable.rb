module CsvSyncer::Modules::Validatable

#
# バリデーションクラス  実装サブクラス毎で実装される
#
private

  def error_row
    @row.map{|r| r[1] }
  end

  def valid?
    return false if !grade_valid?
    return false if !user_orgs_valid?
    true
  end

  # バリデーション処理
  # 本ソースはサンプル判定の実装例
  def grade_valid?
    return true if @row["grades"].present?
    return true if teacher?(@row["role"])
    @errors << error_row.push("学年が空欄です") if @row["role"] != "administrator" #gradesが空で学生
    false
  end

  def user_orgs_valid?
    !user_orgs.any? { |o| o["identifier"] == "A" }
  end

end
