#!/usr/bin/env python
"""
Structural Analysis Package 命令行工具

用法:
    python main.py [command] [options]

命令:
    analyze     - 运行结构分析
    extract     - 提取分析结果
    plot        - 绘制结果图表
"""

import argparse
import sys
from structural_analysis.operations import MidasOperations
from structural_analysis.post_processor import create_processor

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="Structural Analysis Package CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # 添加子命令解析器
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # analyze 命令
    analyze_parser = subparsers.add_parser('analyze', help='运行结构分析')
    analyze_parser.add_argument('--model', required=True, help='模型文件路径 (.mcb)')
    
    # extract 命令
    extract_parser = subparsers.add_parser('extract', help='提取分析结果')
    extract_parser.add_argument('--type', required=True, 
                              choices=['beam_force', 'beam_stress', 'truss_force', 
                                     'cable_force', 'displacement'],
                              help='结果类型')
    extract_parser.add_argument('--elements', required=True, 
                              help='单元编号列表 (例如: 1,2,3)')
    extract_parser.add_argument('--load-case', required=True, 
                              help='荷载工况名称')
    
    # plot 命令
    plot_parser = subparsers.add_parser('plot', help='绘制结果图表')
    plot_parser.add_argument('--type', required=True,
                           choices=['beam_force', 'beam_stress', 'truss_force', 
                                  'cable_force', 'displacement'],
                           help='结果类型')
    plot_parser.add_argument('--elements', required=True,
                           help='单元编号列表 (例如: 1,2,3)')
    plot_parser.add_argument('--load-case', required=True,
                           help='荷载工况名称')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
        
    return args

def run_analysis(args):
    """运行结构分析"""
    if not args.model:
        print("错误: 需要指定模型文件路径")
        return
    
    try:
        # 打开MIDAS Civil并加载模型
        MidasOperations.open_file(
            "C:/Program Files/MIDAS/Civil/Civil.exe",
            args.model
        )
        # 运行分析
        MidasOperations.analyze()
        print("分析完成")
    except Exception as e:
        print(f"分析失败: {str(e)}")

def extract_results(args):
    """提取分析结果"""
    if not all([args.type, args.elements, args.load_case]):
        print("错误: 需要指定结果类型、单元编号和荷载工况")
        return
    
    try:
        processor = create_processor(args.type)
        results = processor.extract_general(
            elems=args.elements.split(','),
            load_case=args.load_case
        )
        print("结果提取成功")
        return results
    except Exception as e:
        print(f"结果提取失败: {str(e)}")

def plot_results(args, results=None):
    """绘制结果图表"""
    if not results:
        results = extract_results(args)
    
    if results:
        try:
            processor = create_processor(args.type)
            df = processor.process_general_results(results)
            processor.plot_results(df)
            print("图表绘制完成")
        except Exception as e:
            print(f"图表绘制失败: {str(e)}")

def main():
    """主函数"""
    args = parse_args()
    
    commands = {
        'analyze': run_analysis,
        'extract': extract_results,
        'plot': plot_results
    }
    
    if args.command in commands:
        commands[args.command](args)
    else:
        print(f"未知命令: {args.command}")

if __name__ == "__main__":
    main()
