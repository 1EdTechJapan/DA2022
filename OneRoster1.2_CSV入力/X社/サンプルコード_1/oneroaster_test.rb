#
# メイン class
#
class CsvSyncer::OneroasterTest < CsvSyncer::Base
# Baseクラスを継承してユースケースごとにクラスを実装する

  #
  # メイン function
  #
  def call
    # ログの開始処理をする
    set_logging
    # 処理開始時間の記録をする
    write_start_time
    # インポート処理をする
    import_user
    # 処理完了時間の記録をする
    write_end_time
  end

private

  # 本サービスの利用ユーザーごとに実装されるfunction
  def assign_tenants
    tenant_user = TenantUser.find_or_create_by(user: @user, tenant: find_or_create_tenant)
    create_tenant_user_role(tenant_user)
    user_orgs.each do |org|
      tenant_group = TenantGroup.find_or_initialize_by(tenant: find_or_create_tenant, name: org["name"])
      TenantGroupTenantUser.find_or_create_by(tenant_group: tenant_group, tenant_user: tenant_user)
    end
  end

  def find_or_create_teacher_role
    Role.find_or_create_by(tenant_id: find_or_create_tenant.id, name: "デジタル庁テスト_先生")
  end

  def find_or_create_student_role
    Role.find_or_create_by(tenant_id: find_or_create_tenant.id, name: "デジタル庁テスト_生徒")
  end

  def find_or_create_tenant
    Tenant.find_or_create_by(name: "デジタル庁テストテナント")
  end

end
