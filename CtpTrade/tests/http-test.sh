#!/usr/bin/env bash

curl -l -H "Content-type: application/json" -X POST -d '["a","b","c"]' http://127.0.0.1:18901/v1/contract/subscribe
curl -l  http://127.0.0.1:18901/v1/contract/list

curl -X POST -d '{"head": {}, "data": {}, "name": "get_all_positions"}' http://127.0.0.1:18900/v1/message/

# 订阅 交易适配器的消息发布接口
redis-cli psubscribe trade.command.channel.trade_adapter.future.htqh-01.pub
