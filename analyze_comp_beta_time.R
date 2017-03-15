
library(ggplot2)
library(reshape)
library(grid)
library(dplyr)


data = read.csv("time_beta_av.csv")
m = melt(data, id=c("beta", "dat_amount", "av_acc", "av_complex"))



m
p <- ggplot(data=m, aes(x=av_complex, y=av_acc, group=beta)) +
  geom_line(aes(color=beta))

p