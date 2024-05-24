module CsvSyncer::Modules::Debugger

#
# ログユーティリティ
#

private

  def set_logging
    @logger = Logger.new(Rails.root.join('log', 'csv_syncer.log'))
  end

  def write_start_time
    @start_time = Time.now
    @logger.debug("start at #{@start_time}")
  end

  def write_end_time
    @end_time = Time.now
    diff = @end_time.to_i - @start_time.to_i
    @logger.debug("end at #{@end_time}")
    @logger.debug("total time is #{diff} seconds")
  end


  def write_time(i)
    @current_time = Time.now
    diff = @current_time.to_i - @start_time.to_i
    @logger.debug("end at #{@current_time}")
    @logger.debug("#{i} finished. #{diff} seconds passed
")
  end

end
