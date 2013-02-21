plotr <- function(output_file, title, start, end) {
    library(RSvgDevice)
    devSVG(file=output_file)
    plot(c(1, 3, 6, 4, 9), type="o", col="blue", main=title, xlab=start, ylab=end)
    dev.off()
}
