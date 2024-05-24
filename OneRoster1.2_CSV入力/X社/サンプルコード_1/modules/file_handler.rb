module CsvSyncer::Modules::FileHandler

#
# ファイル/ディレクトリ ユーティリティ
#
private

  def create_result_dir
    dir = FileUtils.mkdir_p(result_dir)
    dir.first
  end

  def create_download_dir
    dir = FileUtils.mkdir_p(download_dir)
    dir.first
  end

  def fetch_csv_files(container_name: CsvSyncer::Base::CONTAINER_NAME, filename:)
    files    = @blob_client.list_blobs(container_name)
    files.filter!{|con| con.name.include?(filename)}
    files.map!{|f|
      {name: f.name, created_at: f.properties[:creation_Time].to_datetime}
    }
    return if files.blank?

    files.sort! { |a, b|
      a[:created_at] <=> b[:created_at]
    }

    content = @blob_client.get_blob(container_name, files.last[:name])
    File.open("#{download_dir}#{files.last[:name]}", "wb") {|f| f.write(content.last)}
  end

  def result_dir
    "#{Rails.root}/tmp/oneroster/result/"
  end

  def download_dir
    "#{Rails.root}/tmp/oneroster/downloads/"
  end

  def csv_dir
    "#{Rails.root}/tmp/oneroster/csv/"
  end

  def tmp_files
    files = Dir.entries(download_dir)
    files.select {|file| file.include?(".zip") }
  end

  def unzip_file(file)
    Zip::File.open("#{download_dir}#{file}") do |zip|
      dir = unziped_dir(file)
      zip.each do |entry|
        zip.extract(entry, "#{dir}/#{entry.name}") { true }
      end
    end
  end

  def unziped_dir(zipfile)
    file_name = File.basename(zipfile, '.*')
    file_dir  = FileUtils.mkdir_p("#{csv_dir}/#{file_name}")
    file_dir.first
  end

  def clean!
    FileUtils.rm_r(download_dir) if File.exist?(download_dir)
    FileUtils.rm_r(csv_dir)      if File.exist?(csv_dir)
  end

end
