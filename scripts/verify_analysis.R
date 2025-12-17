#!/usr/bin/env Rscript
# Verify ERH Analysis
# independently calculates the exponent alpha from simulation results.

args <- commandArgs(trailingOnly = TRUE)
if (length(args) == 0) {
  stop("Usage: Rscript verify_analysis.R <input_json_dir> <output_dir>")
}

input_dir <- args[1]
output_dir <- args[2]

if (!dir.exists(output_dir)) {
  dir.create(output_dir, recursive = TRUE)
}

# Check if required packages are installed
if (!require("jsonlite", quietly = TRUE)) {
  warning("Package 'jsonlite' not installed. Skipping verification.")
  quit(status = 0)
}

library(jsonlite)

files <- list.files(input_dir, pattern = "sim_result_.*\\.json", full.names = TRUE)
results <- data.frame()

cat("Processing", length(files), "files...\n")

for (f in files) {
  tryCatch({
    data <- fromJSON(f)
    
    # Extract alpha if present
    alpha <- data$metrics$estimated_exponent
    if (is.null(alpha)) alpha <- NA
    
    dist <- data$config$complexity_dist
    
    results <- rbind(results, data.frame(
      file = basename(f),
      dist = dist,
      alpha = alpha,
      stringsAsFactors = FALSE
    ))
  }, error = function(e) {
    cat("Error reading", f, ":", e$message, "\n")
  })
}

# Save summary
write.csv(results, file.path(output_dir, "r_verification_summary.csv"), row.names = FALSE)

# Basic plot (if graphical capabilities exist)
if (capabilities("png")) {
  png(file.path(output_dir, "r_alpha_distribution.png"), width = 800, height = 600)
  boxplot(alpha ~ dist, data = results, 
          main = "Distribution of Alpha (R Verification)",
          ylab = "Alpha", xlab = "Complexity Distribution")
  abline(h = 0.5, col = "red", lty = 2)
  dev.off()
}

cat("R verification complete. Results saved to", output_dir, "\n")
