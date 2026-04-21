#!/usr/bin/env bash
set -e

# ====== 项目根目录 ======
project_root="$(cd "$(dirname "$0")" && pwd)"/..

# ====== LLVM 源码路径（按你实际修改） ======
llvm_src="$project_root/llvm-project/llvm"

# ====== 构建目录 ======
build_dir="$project_root/build-llvm"

# ====== 安装目录（可选，用于干净隔离） ======
install_dir="$project_root/llvm-install"

echo "[INFO] project_root = $project_root"
echo "[INFO] build_dir    = $build_dir"
echo "[INFO] install_dir  = $install_dir"

mkdir -p "$build_dir"
mkdir -p "$install_dir"

# ====== 配置 CMake ======
cmake -G Ninja \
  -S "$llvm_src" \
  -B "$build_dir" \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_PREFIX="$install_dir" \
  -DLLVM_ENABLE_PROJECTS="clang;polly" \
  -DLLVM_TARGETS_TO_BUILD="X86" \
  -DLLVM_INSTALL_UTILS=ON

# ====== 编译 ======
ninja -C "$build_dir" -j 8

echo "[INFO] Build finished."SS