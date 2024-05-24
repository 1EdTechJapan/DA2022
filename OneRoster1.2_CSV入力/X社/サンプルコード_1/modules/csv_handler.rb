module CsvSyncer::Modules::CsvHandler

#
# I/O ユーティリティ
#

private

  def read(file)
    CSV.foreach(file, headers: true)
  end

  # def bulk_files
  #   entries = Dir.entries("#{csv_dir}/#{bulk_dir}")
  #   entries.select{|csv| csv.include?(".csv")}
  # end

  # def delta_files
  #   entries = Dir.entries("#{csv_dir}/#{delta_dir}")
  #   entries.select{|csv| csv.include?(".csv")}
  # end

  def bulk_dir
    entries = Dir.entries(csv_dir)
    entries.find{|f| f.include?("bulk")}
  end

  def delta_dir
    entries = Dir.entries(csv_dir)
    entries.find{|f| f.include?("delta")}
  end

  def create_error_result
	  header = ["sourcedId","status","dateLastModified","enabledUser","orgSourcedIds","role","username","userIds","givenName","familyName","middleName","identifier","email","sms","phone","agentSourcedIds","grades","password","metadata.jp.kanaGivenName","metadata.jp.kanaFamilyName","metadata.jp.kanaMiddleName","metadata.jp.homeClass","エラー内容"]
    File.open("#{result_dir}/errors.csv", 'w:UTF-8') do |file|
      # file.print(bom) # bomを先頭に追加
      file.write "\xEF\xBB\xBF"
      file.write header.to_csv
      @errors.each do |error|
        file.puts(error.to_csv(:force_quotes => true))
      end
    end
  end
end
