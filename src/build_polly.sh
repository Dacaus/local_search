# ====== 项目根目录 ======
project_root="$(cd "$(dirname "$0")" && pwd)"/..

# ====== LLVM 源码路径（按你实际修改） ======
llvm_src="$project_root/llvm-project/llvm"

# ====== 构建目录 ======
build_dir="$project_root/build-llvm"


# ====== 编译 ======
ninja -C "$build_dir" -j 12