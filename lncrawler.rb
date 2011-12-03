#!/usr/bin/env ruby

require 'watir-webdriver'

# TODO
# restrict to some newspaper
# wait until download finished (why not look at the total size of download_dir
# if not possible otherwise...)

class LexisNexisCrawler
  # crawl all the article in Economic News which contain the word 'France'

  def initialize(browser=:chrome, search=['France', 'economie'],
                 sources='French Language News', download_dir='downloads')
    # search: at least one keyword, max 2
    # to download the data where we want
    profile = Selenium::WebDriver::Chrome::Profile.new
    profile['download.prompt_for_download'] = false
    profile['download.default_directory'] = download_dir

    @browser = Watir::Browser.new browser, :profile => profile
    @search = search
    @sources = sources
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
  end

  def crawl_one_day(day, month, year)
    # search
    @browser.link(:text => 'Search').click
    @browser.text_field(:id => 'simpleSearchStyle').set(@search.first)
    @browser.text_field(:name => 'searchTerms2').set(@search.last)
    @browser.select_list(:id => 'sourceDropDown').select(@sources)

    @browser.select_list(:id => 'specifyDateDefaultStyle').select(/Date is/)
    @browser.text_field(:name => 'day1').set(day)
    @browser.select_list(:name => 'month1').select(month)
    @browser.text_field(:name => 'year1').set(year)

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
    @browser.back
  end
end

url = 'https://elib.tcd.ie/login?qurl=http://www.lexisnexis.com/uk/nexis'
crawler = LexisNexisCrawler.new
crawler.login url
crawler.crawl_one_day 20, 'Nov', 2010

