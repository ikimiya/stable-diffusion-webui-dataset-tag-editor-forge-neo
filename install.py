import launch

if not launch.is_installed("open_clip"):
    launch.run_pip("install open-clip-torch", "open-clip-torch requirement for dataset tag editor")