plotr <- function(output_file, title, start, end) {
    library(RSvgDevice)
    devSVG(file=output_file)
    plot(start:end, start:end, main=title, xlab='X', ylab='Y')
    dev.off()
}
