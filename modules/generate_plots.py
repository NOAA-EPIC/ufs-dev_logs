import sys
import os
import json
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from dash_bootstrap_templates import load_figure_template
templates = ["bootstrap",
             "minty",
             "pulse",
             "flatly",
             "quartz",
             "cyborg",
             "darkly",
             "vapor"]
load_figure_template("darkly")

class GeneratePlots():
    """
    Pull-in data tables & generate plots for UFS-WM Regression test & Operation Requirment test logs.
    
    """
    def __init__(self, wall_time_df, test_sz_df):
        """
        Args:                          
            wall_time_df (pd.DataFrame): Wall time per test dataframe

            test_sz_df (pd.DataFrame): Size per test dataframe
            
        """
        # Clone & pull UFS-WM repo
        self.wall_time_df, self.test_sz_df = wall_time_df, test_sz_df

        # Create directory to save results
        if not os.path.exists("plot_results"):
            os.mkdir("plot_results")

    def generate_stacked_barplots(self):
        """
        Generates the stacked bar plots of the relevant log metrics per platform-to-compiler.

        Args:
            None            
            
        Return: None

        """
        # Stacked bar plots for Wall Time (sec) vs Regression Test vs Platform-to-Compiler
        fig = px.bar(self.wall_time_df,
                     x=self.wall_time_df["Test"],
                     y=self.wall_time_df['Wall Time (sec)'],
                     color=self.wall_time_df['Platform_Compiler'],
                     title=f'<b>Wall Time (sec) vs Regression Test per Platform-to-Compiler</b>',
                     color_discrete_sequence=px.colors.qualitative.Light24,
                     width=3000,
                     height=1500,
                     template="darkly")
        
        # Y-axis settings
        fig.update_yaxes(dtick=1000,
                         ticks="outside", 
                         tickwidth=3, 
                         tickcolor='white', 
                         ticklen=5, 
                         col=1,
                         tickprefix="<b>",
                         ticksuffix ="</b><br>",
                         tickfont=dict(family='Helvetica', color='white', size=14))
        
        # X-axis settings
        fig.update_xaxes(ticks="outside", 
                         tickwidth=2, 
                         tickcolor='white', 
                         ticklen=8,
                         tickangle=-90, 
                         tickprefix="<br><b>",
                         ticksuffix ="</b><br>",
                         tickfont=dict(family='Helvetica', color='white', size=9))
        
        # Tick settings
        fig.update_layout(title=dict(x=0.5),
                           legend_title=f'<b>Platform-to-Compiler</b><br>',
                           xaxis_title=f'<b>Regression Test</b><br><br>',
                           yaxis_title=f'<br><br><b>Wall Time (sec)</b>',
                           font=dict(size=18, family='Helvetica'),
                           xaxis={'tickmode':'array', 
                                  'tickvals':self.wall_time_df["Test"]})
        
        # Stacked bar plots for Maximum Resident Size (KB) vs Regression Test vs Platform-to-Compiler
        fig2 = px.bar(self.test_sz_df,
                     x=self.test_sz_df["Test"],
                     y=self.test_sz_df['Max. Resident Set Size (KB)'],
                     color=self.test_sz_df['Platform_Compiler'],
                     title=f'<b>Maximum Resident Set Size (KB) vs Test per Platform-to-Compiler</b>',
                     color_discrete_sequence=px.colors.qualitative.Light24,
                     width=3000,
                     height=1500,
                     template="darkly")
        
        # Y-axis settings
        fig2.update_yaxes(dtick=1000000,
                          ticks="outside", 
                          tickwidth=3, 
                          tickcolor='white', 
                          ticklen=5, 
                          col=1,
                          tickprefix="<br><b>",
                          ticksuffix ="</b><br>",
                          tickfont=dict(family='Helvetica', color='white', size=14))
        
        # X-axis settings
        fig2.update_xaxes(ticks="outside", 
                         tickwidth=1, 
                         tickcolor='white', 
                         ticklen=8,
                         tickangle=-90, 
                         tickprefix="<br><b>",
                         ticksuffix ="</b><br>",
                         tickfont=dict(family='Helvetica', color='white', size=9))
        
        # Tick settings
        fig2.update_layout(title=dict(x=0.5),
                           legend_title=f'<b>Platform-to-Compiler</b><br>',
                           xaxis_title=f'<b>Regression Test</b><br><br>',
                           yaxis_title=f'<br><br><b>Maximum Resident Set Size (KB)</b>',
                           font=dict(size=18, family='Helvetica'),
                           xaxis={'tickmode':'array', 
                                  'tickvals':self.test_sz_df["Test"]})
        
        # Save figures to local
        fig.write_image("plot_results/test_wall_times_stacked.pdf")
        fig2.write_image("plot_results/test_resident_sizes_stacked.pdf")
        print('Bar plots saved to local.')

        return

    def generate_barplots_platform(self):
        """
        Generate test wall & size bar plots per test framework per platform.

        Args:
            None            
            
        Return: None

        """
        
        # Test Wall Time vs all tests performed on each platform (RT Framework)
        filtered2rt_walltime = self.wall_time_df[self.wall_time_df['Test_Framework_Type']=='Regression Test']
        for platform_name in filtered2rt_walltime['Platform'].unique():
            fig = px.bar(filtered2rt_walltime[filtered2rt_walltime['Platform']==platform_name], 
                          x='Test',
                          y='Wall Time (sec)', 
                          color='Compiler',
                          color_discrete_map={'intel': '#24bff2', 'gnu': '#e307f7'},
                          title=f"Wall Times vs Tests Performed on {platform_name}",
                          height=1000, 
                          width=3000)
            fig.update_xaxes(tickmode='linear', 
                              ticks="outside", 
                              tickwidth=1, 
                              tickcolor='white', 
                              ticklen=8,
                              tickangle=-90, 
                              tickprefix="<br><b>",
                              ticksuffix ="</b><br>",
                              tickfont=dict(family='Helvetica', color='white', size=12),
                              categoryorder='category ascending')
            fig.update_yaxes(dtick=100)
            fig.update_layout(font=dict(size=16))
            fig.update_traces(textangle=0, textposition="outside", cliponaxis=False, marker_line_width=0, opacity=1)
            fig.write_image(f"plot_results/WallTimes_by_Platform_RT_{platform_name}.pdf")

        # Test Wall Time vs all tests performed on each platform (OpnReq Framework)
        filtered2opnreq_walltime = self.wall_time_df[self.wall_time_df['Test_Framework_Type']=='Operation Requirement Test']
        for platform_name in filtered2opnreq_walltime['Platform'].unique():
            fig2 = px.bar(filtered2opnreq_walltime[filtered2opnreq_walltime['Platform']==platform_name], 
                          x='Test',
                          y='Wall Time (sec)',
                          color='Compiler',
                          color_discrete_map={'intel': '#24bff2', 'gnu': '#e307f7'},
                          title=f"{platform_name}:<br>Wall Times vs Test Performed",
                          height=1000, 
                          width=2000)
            fig2.update_xaxes(tickmode='linear', 
                              ticks="outside", 
                              tickwidth=1, 
                              tickcolor='white', 
                              ticklen=8,
                              tickangle=-90, 
                              tickprefix="<br><b>",
                              ticksuffix ="</b><br>",
                              tickfont=dict(family='Helvetica', color='white',  size=16),
                              categoryorder='category ascending')
            fig2.update_yaxes(dtick=100)
            fig2.update_layout(font=dict(size=16))
            fig2.update_traces(textangle=0, textposition="outside", cliponaxis=False, marker_line_width=0, opacity=1)
            fig2.write_image(f"plot_results/WallTimes_by_Platform_OpnReq_{platform_name}.pdf")
            
        # Test Size vs all tests performed on each platform (RT Framework)
        filtered2rt_testsz= self.test_sz_df[self.test_sz_df['Test_Framework_Type']=='Regression Test']
        for platform_name in filtered2rt_testsz['Platform'].unique():
            fig3 = px.bar(filtered2rt_testsz[filtered2rt_testsz['Platform']==platform_name], 
                          x='Test',
                          y='Max. Resident Set Size (KB)', 
                          color='Compiler',
                          color_discrete_map={'intel': '#24bff2', 'gnu': '#e307f7'},
                          title=f"Maximum Resident Size vs Tests Performed on {platform_name}",
                          height=1000, 
                          width=3000)
            fig3.update_xaxes(tickmode='linear', 
                              ticks="outside", 
                              tickwidth=1, 
                              tickcolor='white', 
                              ticklen=8,
                              tickangle=-90, 
                              tickprefix="<br><b>",
                              ticksuffix ="</b><br>",
                              tickfont=dict(family='Helvetica', color='white', size=12),
                              categoryorder='category ascending')
            fig3.update_yaxes(dtick=500000)
            fig3.update_layout(font=dict(size=16))
            fig3.update_traces(textangle=0, textposition="outside", cliponaxis=False, marker_line_width=0, opacity=1)
            fig3.write_image(f"plot_results/TestSize_by_Platform_RT_{platform_name}.pdf")

        # Test Size vs all tests performed on each platform (OpnReq Framework)
        filtered2opnreq_testsz = self.test_sz_df[self.test_sz_df['Test_Framework_Type']=='Operation Requirement Test']
        for platform_name in filtered2opnreq_testsz['Platform'].unique():
            fig4 = px.bar(filtered2opnreq_testsz[filtered2opnreq_testsz['Platform']==platform_name], 
                          x='Test',
                          y='Max. Resident Set Size (KB)', 
                          color='Compiler',
                          color_discrete_map={'intel': '#24bff2', 'gnu': '#e307f7'},
                          title=f"{platform_name}:<br>Maximum Resident Size vs Test Performed",
                          height=1000, 
                          width=2000)
            fig4.update_xaxes(tickmode='linear', 
                              ticks="outside", 
                              tickwidth=1, 
                              tickcolor='white', 
                              ticklen=8,
                              tickangle=-90, 
                              tickprefix="<br><b>",
                              ticksuffix ="</b><br>",
                              tickfont=dict(family='Helvetica', color='white', size=16),
                              categoryorder='category ascending')
            fig4.write_image(f"plot_results/TestSize_by_Platform_OpnReq_{platform_name}.pdf")
            fig4.update_layout(font=dict(size=16))
            fig4.update_traces(textangle=0, textposition="outside", cliponaxis=False, marker_line_width=0, opacity=1)
            
        return
        
    def generate_histogramplots(self, df):
        """
        Generates histograms of the relevant log metrics.

        Args:
            None     
            
        Return: None

        """        
        # Plot total tests per test framework type per complier 
        fig = px.histogram(df, 
                           x='Test_Framework_Type',
                           y='Number of Tests',
                           color='Compiler', 
                           color_discrete_map={'intel': '#24bff2', 'gnu': '#e307f7'},
                           barmode='group',
                           text_auto=True,
                           height=800, 
                           width=1000,
                           title="Number of Tests vs UFS-WM Test Frameworks Across Compilers")
        fig.update_yaxes(dtick=200)
        fig.update_xaxes(ticklabelposition='outside bottom',
                         tickfont=dict(family='Helvetica', color='white', size=14))
        fig.update_layout(xaxis_title='Test Framework Type',
                          yaxis_title='Number of Tests', 
                          legend_title_text='Compiler',
                          font = dict(size=14))
        fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False, marker_line_width=0, opacity=1)
        
        # Plot total tests per test framework type per platform (RT Framework)
        fig2 = px.histogram(df[df['Test_Framework_Type']=='Regression Test'],
                            x='Platform',
                            y='Number of Tests',
                            color='Platform',
                            color_discrete_sequence=px.colors.qualitative.Light24,
                            text_auto=True,
                            height=800, 
                            width=1000,
                            title="Regression Test Framework:<br>Number of Tests vs Platform")
        fig2.update_yaxes(dtick=20)
        fig2.update_xaxes(ticklabelposition='outside bottom',
                          tickfont=dict(family='Helvetica', color='white', size=14),
                          categoryorder='category ascending')
        fig2.update_layout(autosize=True,
                           xaxis_title='Platform', 
                           yaxis_title='Number of Tests',
                           font = dict(size=14))
        fig2.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False, marker_line_width=0, opacity=1)
        
        # Plot total tests per test framework type per platform (OpnReq Framework)
        fig3 = px.histogram(df[df['Test_Framework_Type']=='Operation Requirement Test'],
                             x='Platform',
                             y='Number of Tests', 
                             color='Platform',
                             color_discrete_sequence=px.colors.qualitative.Light24,
                             text_auto=True,
                             height=800, 
                             width=1000,
                             title="Operation Test Framework:<br>Number of Tests vs Test-to-Platform")
        fig3.update_xaxes(ticklabelposition='outside bottom',
                          tickfont=dict(family='Helvetica', color='white', size=14),
                          categoryorder='category ascending')  
        fig3.update_layout(xaxis_title='Test-to-Platform', 
                            yaxis_title='Number of Tests', 
                            legend_title_text='Test-to-Platform',
                            font = dict(size=14))
        fig3.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False, marker_line_width=0, opacity=1)
        
         # Plot total tests per platform per compiler per test framework type (RT Framework)
        fig4 = px.bar(df[df['Test_Framework_Type']=='Regression Test'], 
                      y='Number of Tests',
                      x='Platform',
                      color='Compiler',
                      color_discrete_map={'intel': '#24bff2', 'gnu': '#e307f7'},
                      text='Number of Tests',
                      height=800, 
                      width=1000,
                      title="Regression Test Framework:<br>Number of Tests vs Platform")
        fig4.update_yaxes(dtick=20)
        fig4.update_xaxes(ticklabelposition='outside bottom',
                          tickfont=dict(family='Helvetica', color='white', size=14),
                          categoryorder='category ascending')
        fig4.update_layout(xaxis_title='Platform',
                           legend_title_text='Compiler',
                           font = dict(size=14))
        fig4.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False, marker_line_width=0.1, opacity=1)

        fig5 = px.bar(df[df['Test_Framework_Type']=='Operation Requirement Test'], 
                       y='Number of Tests',  
                       x='Platform', 
                       color='Compiler', 
                       color_discrete_map={'intel': '#24bff2', 'gnu': '#e307f7'},
                       text='Number of Tests',
                       height=800, 
                       width=1000,
                       title="Operation Test Framework:<br>Number of Tests vs Test-to-Platform")
        fig5.update_xaxes(ticklabelposition='outside bottom',
                          tickfont=dict(family='Helvetica', color='white', size=14),
                          categoryorder='category ascending')
        fig5.update_layout(xaxis_title='Operation Requirement Test-to-Platform', 
                           legend_title_text='Compiler',
                           font = dict(size=14))
        fig5.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False, marker_line_width=0.1, opacity=1)
        
        # Plot total tests per test-to-platform per compiler per test framework type (OpnReq Framework)
        fig6 = px.bar(df,
                      y='Number of Tests', 
                      x=df.index, 
                      color='Test_Framework_Type',
                      color_discrete_sequence=px.colors.qualitative.Light24,
                      barmode='group',
                      text='Number of Tests',
                      height=800, 
                      width=1000,
                      title="Number of Tests vs Compiler Environment Across Test Framework")
        fig6.update_yaxes(dtick=20)
        fig6.update_xaxes(ticklabelposition='outside bottom',
                          tickfont=dict(family='Helvetica', color='white', size=12))
        fig6.update_layout(xaxis_title='Compiler Environment', 
                           legend_title_text='Test Framework Type',
                           font = dict(size=14))
        fig6.update_traces(width=1, textfont_size=12, textangle=0, textposition="outside", cliponaxis=False, marker_line_width=0.1, opacity=1)
        
        fig.write_image("plot_results/NumOfTests_vs_Framework-to-Compilers_hg.pdf")
        fig.to_json("plot_results/testing_json")
        fig2.write_image("plot_results/RT_NumOfTests_vs-Platform_hg.pdf")
        fig3.write_image("plot_results/Opnreq_NumOfTests_vs_TestName-to-Platform_hg.pdf")
        fig4.write_image("plot_results/RT_NumOfTests_vs_Platform-to-Comp_bar.pdf")
        fig5.write_image("plot_results/Opnreq_NumOfTests_vs_TestName-to-Platform_bar.pdf")
        fig6.write_image("plot_results/NumOfTests_vsCompilerEnvironment_bar.pdf")
        print('Histogram plots saved to local.')
        
        return
