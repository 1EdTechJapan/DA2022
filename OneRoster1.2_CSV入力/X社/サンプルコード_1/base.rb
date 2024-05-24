#
# OneRosterCSV 基底クラス
#
class CsvSyncer::Base
  require 'zip'
  require "csv"
  include CsvSyncer::Modules::FileHandler
  include CsvSyncer::Modules::CsvHandler
  include CsvSyncer::Modules::Importable
  include CsvSyncer::Modules::Validatable
  include CsvSyncer::Modules::Debugger

  CONTAINER_NAME = "oneroster".freeze

  def initialize
    @blob_client = Azure::Storage::Blob::BlobService.create(
                    # データの連携先を設定している
                    # 本ソースでは一例
                    storage_account_name: Rails.application.credentials.microsoft[:storage_account_name],
                    storage_access_key: Rails.application.credentials.microsoft[:storage_access_key]
                  )
    @errors = []
  end

end
