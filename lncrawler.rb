#!/usr/bin/env ruby

require 'date'
require 'watir-webdriver'

class LexisNexisCrawler
  # crawl all the article in Economic News which contain the word 'France'
  attr_accessor :search  # search terms, array of one or two keywords
                         # default to %w(France economie)
  attr_accessor :source  # e.g. (default):"French Language News"
  attr_accessor :indexes # indexes of the checkbox to check, default to [0]

  def initialize(browser=:chrome, download_dir='downloads')
    profile = Selenium::WebDriver::Chrome::Profile.new
    profile['download.prompt_for_download'] = false
    profile['download.default_directory'] = download_dir

    @browser = Watir::Browser.new browser, :profile => profile
    @search = %w(France economie)
    @source = 'French Language News'
    @indexes = [0]
  end

  def login(url, user='', pass='')
    # ask for login details for login details before going to login
    # page, so once it's filed user can go away
    # obviously if login details are provided to the method, doesn't ask
    while user.empty? or pass.empty?
      puts 'Username:'
      user = gets.chomp
      puts 'Password:'
      pass = gets.chomp
    end

    # goto login page
    @browser.goto url

    @browser.text_field(:name => 'user').set(user)
    @browser.text_field(:name => 'pass').set(pass)
    @browser.button(:name => 'Submit2').click

    # accept term & conditions
    @browser.link(:href => /submitterms\.do/).click

    # get the search link
    @searchUrl = @browser.link(:text => 'Search').href
  end

  def crawl(from, to)
    # crawl all the article from from to to (Date objects)
    until from > to
      begin
        crawl_one_day from
      rescue Exception => e
        if @browser.text.include? 'No Documents Found'
          STDERR.puts "[INFO] #{from.to_s} - No document found."
        else
          STDERR.puts "[ERROR] #{from.to_s} - Something unexpected happened while crawling."
          STDERR.puts "                       #{e.message}"
          STDERR.puts e.backtrace.inspect
        end
      end
      from = from.next_day
    end
  end

  def crawl_one_week(date)
    7.times do
      begin
        crawl_one_day date
      rescue Exception => e
        if @browser.text.include? 'No Documents Found'
          STDERR.puts "[INFO] #{date.to_s} - No document found."
        else
          STDERR.puts "[ERROR] #{date.to_s} - Something unexpected happened while crawling."
          STDERR.puts "                       #{e.message}"
          STDERR.puts e.backtrace.inspect
        end
      end
      date = date.next_day
    end
  end

  def crawl_one_day(date)
    STDERR.puts "[INFO] #{date.to_s} - Crawling."
    # search
    @browser.goto @searchUrl
    @browser.text_field(:id => 'simpleSearchStyle').set(@search.first)
    @browser.text_field(:name => 'searchTerms2').set(@search.last)
    @browser.select_list(:id => 'sourceDropDown').select(@source)

    # select newspapers/websites
    @indexes.each do |idx|
      @browser.div(:id => 'hiddenDivsourceList').checkbox(:index => idx).set
    end

    @browser.select_list(:id => 'specifyDateDefaultStyle').select(/Date is/)
    @browser.text_field(:name => 'day1').set(date.day)
    @browser.select_list(:name => 'month1').select(date.strftime('%b'))
    @browser.text_field(:name => 'year1').set(date.year)

    @browser.image(:id => 'enableSearchImg').click

    # find & click download link
    @browser.frame(:title => 'Results Navigation Frame').link(:href => /delivery_DnldRender/).click

    # download options
    url = ''
    @browser.window(:title => /download/i).use do
      @browser.select_list(:name => 'delFmt').select('Text')
      @browser.link(:href => /delivery_DnldForm/).click

      sleep 1 until @browser.text.include? '.TXT'

      url = @browser.link(:text => /\.TXT/).href
    end

    @browser.window(:title => /download/i).close
    @browser.goto url
  end

  def close
    @browser.close
  end
end

### let the magic happen ###

url = 'https://elib.tcd.ie/login?qurl=http://www.lexisnexis.com/uk/nexis'
crawler = LexisNexisCrawler.new
crawler.indexes = [10, 17, 39, 59, 60, 86, 102, 144, 157, 186, 190]
# afp, agefi quotidien, boursier.com, les echos,
# lesechos.fr, le figaro économie, investir.fr,
# le parisien économie, radiobfm.com,
# la tribune, latribune.fr
crawler.login url
#crawler.crawl Date.new(1999, 12, 30), Date.new(2000, 1, 2)
crawler.crawl_one_week Date.new(2005, 01, 01)
crawler.close

