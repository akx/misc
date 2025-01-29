use clap::Parser;
use std::fs::File;
use std::io::Read;
use std::os::unix::fs::MetadataExt;
use std::path::PathBuf;
use rayon::prelude::*;

#[derive(Parser)]
/// Find files that are all zeroes in the given directory.
struct Opts {
    path: PathBuf,

    #[clap(short, long)]
    /// Delete the found all-zero files.
    delete: bool,
}

fn main() {
    let opts: Opts = Opts::parse();
    let mut file_paths: Vec<PathBuf> = vec![];
    for f in walkdir::WalkDir::new(opts.path).into_iter().flatten() {
        if f.file_type().is_file() && f.metadata().unwrap().size() > 0 {
            file_paths.push(f.path().to_path_buf());
        }
    }
    eprintln!("Found {} files to consider", file_paths.len());
    let zero_bytes_files = file_paths.par_iter().filter(|pth| is_all_zeroes(pth)).collect::<Vec<_>>();
    for zero_pth in zero_bytes_files.iter() {
        println!("{}", zero_pth.display());
        if opts.delete {
            std::fs::remove_file(zero_pth).unwrap();
        }
    }
    eprintln!("{} zero-byte files out of {}", zero_bytes_files.len(), file_paths.len());
}

fn is_all_zeroes(pth: &PathBuf) -> bool {
    let mut file = File::open(pth).unwrap();
    let mut initial_buf = [0; 64];
    let num_read = file.read(&mut initial_buf).unwrap();
    if initial_buf[..num_read].iter().any(|&x| x != 0) {
        return false;
    }
    loop {
        let mut buf = [0; 1024];
        let num_read = file.read(&mut buf).unwrap();
        if num_read == 0 {
            break;
        }
        if buf[..num_read].iter().any(|&x| x != 0) {
            return false;
        }
    }
    true
}
