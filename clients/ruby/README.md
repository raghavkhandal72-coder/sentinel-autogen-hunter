# Sentinel-AutoGen-Hunter Ruby SDK

Enterprise Ruby SDK Client for Sentinel-AutoGen-Hunter autonomous multi-agent threat hunting, deception grid, and gateway orchestrator.

## Installation

Configure RubyGems to install from GitHub Packages:

```bash
gem install sentinel-autogen-hunter --source https://rubygems.pkg.github.com/raghavkhandal72-coder
```

Or add to your `Gemfile`:

```ruby
source "https://rubygems.pkg.github.com/raghavkhandal72-coder" do
  gem "sentinel-autogen-hunter", "~> 1.4.1"
end
```

## Quick Start

```ruby
require 'sentinel/hunter'

client = Sentinel::Client.new('http://localhost:8000')
puts client.health
```
