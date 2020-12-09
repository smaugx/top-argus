# top-argus

top-argus 是⼀个开源的分布式监控系统框架，采⽤ python 编写，模块化设计，分为 agent/proxy/consumer/dash 等模块，每个模块⽀持⼀定程度的定制化。后端使⽤ redis 进⾏缓存，⼆
次处理之后持久化到 mysql。根据采集压⼒，可增加机器作为集群进⾏消费处理。

