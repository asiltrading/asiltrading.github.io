source "https://rubygems.org"

# GitHub Pages-compatible Jekyll. Pinning to github-pages gem ensures
# our local builds match what GitHub renders.
gem "github-pages", group: :jekyll_plugins

group :jekyll_plugins do
  gem "jekyll-seo-tag"
  gem "jekyll-sitemap"
  gem "jekyll-redirect-from"
end

# Platform-specific dependencies
gem "tzinfo-data", platforms: [:mingw, :mswin, :x64_mingw, :jruby]
gem "wdm", "~> 0.1.1", platforms: [:mingw, :mswin, :x64_mingw]

# webrick is no longer in Ruby's stdlib from 3.0
gem "webrick", "~> 1.8"
