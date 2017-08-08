## Storm Real-time Computing Cluster For Knowing

本仓库存放用于 [Knowing][1] 数据来源的实时计算集群。本项目基于 [Apache Storm][2] 。

## TODO

* 将 package 名字从 `com.tower.hello` 改成其他，例如 `com.tower.corp.knowing.topologies` 。

## Quick Start

TODO: vagrant & provision

### 安装 JDK 与 jzmq

JDK 如无特殊情况，推荐使用 Oracle JDK 1.7。（1.6 以及 Icedtea 1.7 ， 1.6 也可工作，但尽量与生产环境保持一致）。

根据 storm 的版本，安装对应的 jzmq 版本，可以在 storm jar 包或源代码的 pom.xml 看到依赖的 jzmq 版本。

**目前 storm-0.8.1 依赖 jzmq-2.1.0 版**

```
$ git clone https://github.com/zeromq/jzmq
$ cd jzmq
$ git checkout v2.1.0
$ ./autogen.sh
$ ./configure "--prefix=/usr"
$ make # 注意不能用 -j 大于 1 的参数，目前并行编译会有问题
$ (sudo) make install
```

**Gentoo 用户可以直接使用这个 overlay ： https://github.com/aleiphoenix/cirno-overlay 。**

```
$ emerge -v =net-libs/jzmq-2.1.0
```

### 安装 maven

推荐安装 maven>=3.0

### 获取源代码、安装依赖

配置 maven 镜像，采用如下配置文件，放置于 `~/.m2/settings.xml`

```
<settings xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
        http://maven.apache.org/xsd/settings-1.0.0.xsd">
  <mirrors>
    <mirror>
      <id>office</id>
      <name>office</name>
      <url>http://10.10.3.225/nexus/content/groups/public</url>
      <mirrorOf>central</mirrorOf>
    </mirror>
  </mirrors>
</settings>
```

```
$ git clone git://git.corp.tower.com/_knowing/storm-topologies
$ mvn clean install assembly:assembly -DskipTests=true
```

### 数据源依赖

请安装 python2.7 ， libzmq>=2.1 以及 virtualenv

```
$ cd puppy
$ virtualenv --no-site-packages .virtualenv
$ .virtualenv/bin/python setup.py develop
```

### 运行

storm 本身的 topologies 只负责实时计算，数据源在外部，故需要再运行一个数据源。

以 AccessLogTopology 的数据源举例，在项目根目录运行

```
$ ./pp lbalpush.py
```

再运行对应的 Topology

```
$ mvn exec:java -Dexec.mainClass=com.tower.storm.hello.AccessLogTopology

# 或者
$ java -cp target/storm-hello-1.0-fffffff-dev-jar-with-dependencies.jar com.tower.hello.AccessLogTopology
```


[1]: http://git.corp.tower.com/_knowing/sakuya
[2]: https://storm.incubator.apache.org/
