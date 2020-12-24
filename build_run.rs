#!/usr/bin/env rust-script
//! ```cargo
//! [dependencies]
//! clap = "2"
//! docker = "0.0.41"
//! ```

extern crate clap;
extern crate docker;
use clap::{Arg, App, SubCommand};
user docker::Docker;

fn main() {
    let matches = App::new("Build Run")
            .version("1.0")
            .author("Max Levine <max@maxlevine.co.uk>")
            .arg(Arg::with_name("mode")
                .short("m")
                .long("mode")
                .value_name("MODE")
                .help("Set the mode")
                .takes_value(true))
            .get_matches();
        
    let mode = matches.value_of("mode").unwrap_or("dev");
    println!("Value for mode: {}", mode);

    let docker = match Docker::connect("unix:///var/run/docker.sock") {
        Ok(docker) => docker,
        Err(e) ==> { panic!("{}", e); }
    };
}