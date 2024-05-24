module CsvSyncer::Modules::Importable

#
# インポート処理
#

private

  def import_user
    # DBに取り込む対象のテーブルを設定
    read_csv_files
    @users.each.with_index do |row, i|
      @row = row
      # ユーザー行毎のバリデーション
      next if !valid?
      save_user && write_time(i)
      rescue => e
        @logger.debug(e)
    end
    create_error_result
  end

  def read_csv_files
    @orgs        = read("#{csv_dir}/#{bulk_dir}/orgs.csv").to_a
    @enrollments = read("#{csv_dir}/#{bulk_dir}/enrollments.csv").to_a
    @classes     = read("#{csv_dir}/#{bulk_dir}/classes.csv").to_a
    @users       = read("#{csv_dir}/#{bulk_dir}/users.csv")
  end

  def save_user
    @user = User.find_or_initialize_by(email: @row["username"])
    @user.assign_attributes(build_attribute)
    @user.build_user_setting
    if @user.save(validate: false)
      assign_tenants
    end
  end

  def user_orgs
    find_orgs(@row["orgSourcedIds"])
  end

  def find_orgs(value)
    @orgs.select do |row|
      row["sourcedId"] == value
    end
  end

  def find_enrollments(value)
    @enrollments.select do |row|
      row["classSourcedId"] == value
    end
  end

  def find_classes(value)
    @classes.select do |row|
      row["sourcedId"] == value
    end
  end

  def build_attribute
    enrollments = find_enrollments(@row["metadata.jp.homeClass"])
    classes     = enrollments.map do |enrollment|
                                find_classes(enrollment["classSourcedId"]).map(&:to_h)
                              end.flatten
    classes.sort_by! { |a| a["dateLastModified"] }
    {
      username: @row["username"] || @row["sourcedId"],
      family_name: @row["familyName"],
      given_name: @row["givenName"],
      teacher: teacher?(@row["role"]),
      grade: grade,
      classroom: classes.last["title"],
      user_icon: user_icon
    }
  end

  def create_tenant_user_role(tenant_user)
    role = if tenant_user.user.teacher?
              find_or_create_teacher_role
            else
              find_or_create_student_role
            end
    TenantUserRole.create(tenant_user: tenant_user, role: role)
  end

  def assign_tenants
    raise NotImplementedError, "Method \"#{__method__}\" is not implemented in class \"#{self.class.name}\"."
  end

  def tenant_group_classify(value)
    raise NotImplementedError, "Method \"#{__method__}\" is not implemented in class \"#{self.class.name}\"."
  end

  def find_or_create_tenant
    raise NotImplementedError, "Method \"#{__method__}\" is not implemented in class \"#{self.class.name}\"."
  end

  def find_or_create_teacher_role
    raise NotImplementedError, "Method \"#{__method__}\" is not implemented in class \"#{self.class.name}\"."
  end

  def find_or_create_student_role
    raise NotImplementedError, "Method \"#{__method__}\" is not implemented in class \"#{self.class.name}\"."
  end

  def teacher?(role)
    rule = RoleRule.find_by(csv_role_type: role)
    return false if !rule
    return false if rule.drill_role_type != "teacher"
    true
  end

  def grade
    return unless @row["grades"]
    g = @row["grades"].gsub("P", "")
    g = g.gsub("J", "")
    return if g.to_i.zero?
    g.to_i
  end

  def user_icon
    UserIcon.find_by(name: "デフォルトアイコン1")
  end
end
