import sys
import os
import json
import random
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from colormap import rgb2hex, rgb2hls, hls2rgb
from dash_bootstrap_templates import load_figure_template
templates = ["bootstrap",
             "darkly",
             "lux"]
load_figure_template("lux")

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
            
        # Colors allowed
        self.acceptable_colors()
        
    def hex_to_rgb(self, hex):
        '''
        
        Args:
            hex (str): Color's hex.
            
        Return (tuple): Color's RGB values 
        
        '''
        hex = hex.lstrip('#')
        hlen = len(hex)
        
        return tuple(int(hex[i:i+hlen//3], 16) for i in range(0, hlen, hlen//3))
        
    def adjust_color_lightness(self, r, g, b, factor):
        '''
        Vary brightness of a RGB as needed.
        
        Args:
             r (int): Red value
             
             g (int): Green value
             
             b (int): Blue value
             
             factor (float): Level of brightness.
            
        Return (str): Adjusted color in hex.
        
        '''
        h, l, s = rgb2hls(r/255.0, g/255.0, b/255.0)
        l = max(min(l * factor, 1.0), 0.0)
        r, g, b = hls2rgb(h, l, s)
        
        return rgb2hex(int(r*255), int(g*255), int(b*255))
    
    def adjust_color_darkness(self, r, g, b, factor):
        '''
        Vary darkness of a RGB as needed.
        
        Args:
             r (int): Red value
             
             g (int): Green value
             
             b (int): Blue value
             
             factor (float): Level of darkness.
            
        Return (str): Adjusted color in hex.
        
        '''
        return self.adjust_color_lightness(r, g, b, 1-factor)

    def acceptable_colors(self, custom_hex_list = ['#0A4595', '#D87327', '#00A54F', '#89DCFF']):
        '''
        [Optional] Generates variations of the NOAA EPIC acceptable colors.
        
        Arg (list): 
             custom_hex_list (list): List of Hex colors. 
                                     Default: List of NOAA EPIC acceptable hex colors.
            
        Return: None

        Sample of shades:
        ['#4B92F2', '#D87327', '#61D0FF', '#00A54F', '#89DCFF', '#04224A', '#4BFEA1', 
        '#3AC4FE', '#AC5C1F', '#EBB993', '#6C3913', '#0F67DF', '#0A4595']
        
        '''
        light_spectrum_list = []
        dark_spectrum_list = []
        for hex_color in custom_hex_list:
            r, g, b = self.hex_to_rgb(hex_color) # hex to rgb format
            light_spectrum_list.extend([self.adjust_color_lightness(r, g, b, factor=x/100) for x in range(0, 300, 3)])

        # Visible colors within acceptable range
        self.acceptable_colors_list =[]
        for i in list(light_spectrum_list[i] for i in list(range(1, len(light_spectrum_list), 1))):
            self.acceptable_colors_list.append(i)
            
        return
        
    def generate_stacked_barplots(self, x_font_sz=9, y_font_sz=14, fontname='Helvetica', txt_color='#000000', bg_color='#FFFFFF'):
        """
        Generates the stacked bar plots of the relevant log metrics per platform-to-compiler.

        Args:
            x_font_sz (float): Font size of the x-axis.
            
            y_font_sz (float): Font size of the y axis.   

            fontname (str): Font style.

            txt_color (str): Hex color for font.

            bg_color (str): Hex color for plot background.
            
        Return: None

        """
        # Stacked bar plots for Wall Time vs Regression Test vs Platform-to-Compiler
        fig = px.bar(self.wall_time_df,
                     x=self.wall_time_df["Test"],
                     y=self.wall_time_df['Wall Time (min)'],
                     color=self.wall_time_df['Platform_Compiler'],
                     title=f'<b>Wall Time (min) vs Regression Test per Platform-to-Compiler</b>',
                     color_discrete_sequence=px.colors.qualitative.Dark24,
                     width=3000,
                     height=1500,
                     template="lux")
        
        # Y-axis settings
        fig.update_yaxes(ticks="outside", 
                         tickwidth=3, 
                         tickcolor=txt_color, 
                         ticklen=5, 
                         col=1,
                         tickprefix="<b>",
                         ticksuffix ="</b><br>",
                         tickfont=dict(family=fontname,
                                       color=txt_color,
                                       size=y_font_sz))
        
        # X-axis settings
        fig.update_xaxes(ticks="outside", 
                         tickwidth=2, 
                         tickcolor=txt_color, 
                         ticklen=8,
                         tickangle=-90, 
                         tickprefix="<br><b>",
                         ticksuffix ="</b><br>",
                         tickfont=dict(family=fontname,
                                       color=txt_color, 
                                       size=x_font_sz))
        
        # Tick settings
        fig.update_layout(title=dict(x=0.5),
                           legend_title=f'<b>Platform-to-Compiler</b><br>',
                           xaxis_title=f'<b>Regression Test</b><br><br>',
                           yaxis_title=f'<br><br><b>Wall Time (min)</b>',
                           font=dict(family=fontname, 
                                     size=18),
                           xaxis={'tickmode':'array', 
                                  'tickvals':self.wall_time_df["Test"]})
        
        # Stacked bar plots for Maximum Resident Size vs Regression Test vs Platform-to-Compiler
        fig2 = px.bar(self.test_sz_df,
                     x=self.test_sz_df["Test"],
                     y=self.test_sz_df['Max Resident Set Size (MB)'],
                     color=self.test_sz_df['Platform_Compiler'],
                     title=f'<b>Maximum Resident Set Size vs Test per Platform-to-Compiler</b>',
                     color_discrete_sequence=px.colors.qualitative.Dark24,
                     width=3000,
                     height=1500,
                     template="lux")
        
        # Y-axis settings
        fig2.update_yaxes(ticks="outside", 
                          tickwidth=3, 
                          tickcolor=txt_color, 
                          ticklen=5, 
                          col=1,
                          tickprefix="<br><b>",
                          ticksuffix ="</b><br>",
                          tickfont=dict(family=fontname,
                                        color=txt_color,
                                        size=y_font_sz))
        
        # X-axis settings
        fig2.update_xaxes(ticks="outside", 
                         tickwidth=1, 
                         tickcolor=txt_color, 
                         ticklen=8,
                         tickangle=-90, 
                         tickprefix="<br><b>",
                         ticksuffix ="</b><br>",
                         tickfont=dict(family=fontname,
                                       color=txt_color,
                                       size=x_font_sz))
        
        # Tick settings
        fig2.update_layout(title=dict(x=0.5),
                           legend_title=f'<b>Platform-to-Compiler</b><br>',
                           xaxis_title=f'<b>Regression Test</b><br><br>',
                           yaxis_title=f'<br><br><b>Maximum Resident Set Size (MB)</b>',
                           font=dict(family=fontname,
                                     size=18),
                           xaxis={'tickmode':'array', 
                                  'tickvals':self.test_sz_df["Test"]})
        
        # Save figures to local
        fig.write_image("plot_results/test_wall_times_stacked.pdf")
        fig2.write_image("plot_results/test_resident_sizes_stacked.pdf")
        print('Bar plots saved to local.')

        return

    def generate_barplots_platform(self, x_font_sz=14, y_font_sz=14, fontname='Helvetica', txt_color='#000000', bg_color='#FFFFFF'):
        """
        Generate test wall & size bar plots per test framework per platform.

        Args:
            x_font_sz (float): Font size of the x-axis.
            
            y_font_sz (float): Font size of the y axis.   

            fontname (str): Font style.

            txt_color (str): Hex color for font.

            bg_color (str): Hex color for plot background.
            
        Return: None

        """
        
        # Test Wall Time vs all tests performed on each platform (RT Framework)
        filtered2rt_walltime = self.wall_time_df[self.wall_time_df['Test_Framework_Type']=='Regression Testing']
        for platform_name in filtered2rt_walltime['Platform'].unique():
            fig = px.bar(filtered2rt_walltime[filtered2rt_walltime['Platform']==platform_name], 
                          x='Test',
                          y='Wall Time (min)', 
                          color='Compiler',
                          color_discrete_map={'intel': '#61D0FF', 'gnu': '#D87327'},
                          title=f"Regression Test Framework:<br>Wall Times vs Tests Performed on {platform_name}",
                          height=1000, 
                          width=3000)
            fig.update_yaxes(tickfont=dict(family=fontname,
                                           color=txt_color,
                                           size=y_font_sz))
            fig.update_xaxes(tickmode='linear', 
                              ticks="outside", 
                              tickwidth=1, 
                              tickcolor=txt_color,
                              ticklen=8,
                              tickangle=-90,
                              tickfont=dict(family=fontname, 
                                            color=txt_color, 
                                            size=x_font_sz),
                              categoryorder='category ascending')
            #fig.update_yaxes(dtick=100)
            fig.update_layout(title_font_family=fontname,
                              font=dict(size=16), 
                              plot_bgcolor=bg_color)
            fig.update_traces(textangle=0, textposition="outside", cliponaxis=False, marker_line_width=0, opacity=1)
            fig.write_image(f"plot_results/WallTimes_by_Platform_RT_{platform_name}.pdf")

        # Test Wall Time vs all tests performed on each platform (OpnReq Framework)
        filtered2opnreq_walltime = self.wall_time_df[self.wall_time_df['Test_Framework_Type']=='Operation Requirement Test']
        for platform_name in filtered2opnreq_walltime['Platform'].unique():
            fig2 = px.bar(filtered2opnreq_walltime[filtered2opnreq_walltime['Platform']==platform_name], 
                          x='Test',
                          y='Wall Time (min)',
                          #color='Compiler', # No longer featured in Opn Req logs
                          title=f"Operation Requirement Test Framework:<br>Wall Times vs Test Performed on {platform_name}",
                          height=1000, 
                          width=2000)
            fig2.update_yaxes(tickfont=dict(family=fontname,
                                            color=txt_color,
                                            size=y_font_sz))
            fig2.update_xaxes(tickmode='linear', 
                              ticks="outside", 
                              tickwidth=1, 
                              tickcolor=txt_color, 
                              ticklen=8,
                              tickangle=-90,
                              tickfont=dict(family=fontname,
                                            color=txt_color, 
                                            size=x_font_sz),
                              categoryorder='category ascending')
            #fig2.update_yaxes(dtick=100)
            fig2.update_layout(title_font_family=fontname,
                               font=dict(size=16),
                               plot_bgcolor=bg_color)
            fig2.update_traces(marker_color='#0A4595',
                               textangle=0,
                               textposition="outside",
                               cliponaxis=False, 
                               marker_line_width=0, 
                               opacity=1)
            fig2.write_image(f"plot_results/WallTimes_by_Platform_OpnReq_{platform_name}.pdf")
            
        # Test Size vs all tests performed on each platform (RT Framework)
        filtered2rt_testsz= self.test_sz_df[self.test_sz_df['Test_Framework_Type']=='Regression Testing']
        for platform_name in filtered2rt_testsz['Platform'].unique():
            fig3 = px.bar(filtered2rt_testsz[filtered2rt_testsz['Platform']==platform_name], 
                          x='Test',
                          y='Max Resident Set Size (MB)', 
                          color='Compiler',
                          color_discrete_map={'intel': '#61D0FF', 'gnu': '#D87327'},
                          title=f"Regression Test Framework:<br>Maximum Resident Size vs Tests Performed on {platform_name}",
                          height=1000, 
                          width=3000)
            fig3.update_yaxes(tickfont=dict(family=fontname,
                                            color=txt_color,
                                            size=y_font_sz)
                              #dtick=500000
                             )
            fig3.update_xaxes(tickmode='linear', 
                              ticks="outside", 
                              tickwidth=1, 
                              tickcolor=txt_color, 
                              ticklen=8,
                              tickangle=-90,
                              tickfont=dict(family=fontname,
                                            color=txt_color, 
                                            size=x_font_sz),
                              categoryorder='category ascending')
            fig3.update_layout(title_font_family=fontname,
                               font=dict(size=16),
                               plot_bgcolor=bg_color)
            fig3.update_traces(textangle=0, textposition="outside", cliponaxis=False, marker_line_width=0, opacity=1)
            fig3.write_image(f"plot_results/TestSize_by_Platform_RT_{platform_name}.pdf")

        # Test Size vs all tests performed on each platform (OpnReq Framework)
        filtered2opnreq_testsz = self.test_sz_df[self.test_sz_df['Test_Framework_Type']=='Operation Requirement Test']
        for platform_name in filtered2opnreq_testsz['Platform'].unique():
            fig4 = px.bar(filtered2opnreq_testsz[filtered2opnreq_testsz['Platform']==platform_name], 
                          x='Test',
                          y='Max Resident Set Size (MB)',
                          title=f"Operation Requirement Test Framework:<br>Maximum Resident Size vs Test Performed on {platform_name}",
                          height=1000, 
                          width=2000)
            fig4.update_yaxes(tickfont=dict(family=fontname,
                                            color=txt_color,
                                            size=y_font_sz))
            fig4.update_xaxes(tickmode='linear', 
                              ticks="outside", 
                              tickwidth=1, 
                              tickcolor=txt_color, 
                              ticklen=8,
                              tickangle=-45,
                              tickfont=dict(family=fontname,
                                            color=txt_color,
                                            size=x_font_sz),
                              categoryorder='category ascending')
            fig4.update_layout(title_font_family=fontname,
                               font=dict(size=18),
                               plot_bgcolor=bg_color)
            fig4.update_traces(marker_color='#0A4595',
                               textangle=0, 
                               textposition="outside", 
                               cliponaxis=False, 
                               marker_line_width=0,
                               opacity=1)
            fig4.write_image(f"plot_results/TestSize_by_Platform_OpnReq_{platform_name}.pdf")
            
        return
        
    def generate_histogramplots(self, df, x_font_sz=14, y_font_sz=14, fontname='Helvetica', txt_color='#000000', bg_color='#FFFFFF'):
        """
        Generates histograms of the relevant log metrics.

        Args:
            x_font_sz (float): Font size of the x-axis.
            
            y_font_sz (float): Font size of the y axis.   

            fontname (str): Font style.

            txt_color (str): Hex color for font.

            bg_color (str): Hex color for plot background.
            
        Return: None

        """        
        # Plot total tests per test framework type per complier 
        fig = px.histogram(df, 
                           x='Test_Framework_Type',
                           y='Number of Tests',
                           color='Compiler', 
                           color_discrete_map={'intel': '#61D0FF', 'gnu': '#D87327'},
                           barmode='group',
                           text_auto=True,
                           height=800, 
                           width=1000,
                           title="Number of Tests vs UFS-WM Test Frameworks Across Compilers")
        fig.update_yaxes(tickfont=dict(family=fontname,
                                        color=txt_color,
                                        size=y_font_sz))
        fig.update_xaxes(ticklabelposition='outside bottom',
                          tickfont=dict(family=fontname,
                                        color=txt_color,
                                        size=x_font_sz))
        fig.update_layout(xaxis_title='Test Framework Type',
                          yaxis_title='Number of Tests', 
                          legend_title_text='Compiler',
                          title_font_family=fontname,
                          font=dict(size=14),
                          plot_bgcolor=bg_color,
                          paper_bgcolor=bg_color)
        fig.update_traces(textfont_size=12, 
                          textangle=0, 
                          textposition="outside", 
                          cliponaxis=False, 
                          marker_line_width=0, 
                          opacity=1)
        
        # Plot total tests per test framework type per platform (RT Framework)
        fig2 = px.histogram(df[df['Test_Framework_Type']=='Regression Testing'],
                            x='Platform',
                            y='Number of Tests',
                            color='Platform',
                            color_discrete_sequence=px.colors.qualitative.Light24,
                            text_auto=True,
                            height=800, 
                            width=1000,
                            title="Regression Test Framework:<br>Number of Tests vs Platform")
        fig2.update_yaxes(tickfont=dict(family=fontname,
                                        color=txt_color,
                                        size=y_font_sz)
                          #dtick=20
                         )
        fig2.update_xaxes(ticklabelposition='outside bottom',
                          tickfont=dict(family=fontname, 
                                        color=txt_color, 
                                        size=x_font_sz),
                          categoryorder='category ascending')
        fig2.update_layout(autosize=True,
                           xaxis_title='Platform', 
                           yaxis_title='Number of Tests',
                           title_font_family="Helvetica",
                           font=dict(size=14),
                           plot_bgcolor=bg_color,
                           paper_bgcolor=bg_color)
        fig2.update_traces(textfont_size=12,
                           textangle=0,
                           textposition="outside", 
                           cliponaxis=False,
                           marker_line_width=0, 
                           opacity=1)
        
        # Plot total tests per platform (OpnReq Framework)
        fig3 = px.bar(df[df['Test_Framework_Type']=='Operation Requirement Test'], 
                       y='Number of Tests',  
                       x='Platform', 
                       #color='Compiler', 
                       #color_discrete_map=px.colors.qualitative.Dark24,
                       text='Number of Tests',
                       height=800, 
                       width=1000,
                       title="Operation Test Framework:<br>Number of Platform")
        fig3.update_yaxes(tickfont=dict(family=fontname,
                                        color=txt_color,
                                        size=y_font_sz))
        fig3.update_xaxes(ticklabelposition='outside bottom',
                          tickfont=dict(family=fontname,
                                        color=txt_color,
                                        size=x_font_sz),
                          categoryorder='category ascending')
        fig3.update_layout(xaxis_title='Platform',
                           legend_title_text='Compiler',
                           title_font_family=fontname,
                           font=dict(size=14),
                           plot_bgcolor=bg_color,
                           paper_bgcolor=bg_color)
        fig3.update_traces(marker_color='#0f67df',
                           textfont_size=12,
                           textangle=0, 
                           textposition="outside", 
                           cliponaxis=False,
                           marker_line_width=0.1, 
                           opacity=1)
        
         # Plot total tests per platform per compiler per test framework type (RT Framework)
        fig4 = px.bar(df[df['Test_Framework_Type']=='Regression Testing'], 
                      y='Number of Tests',
                      x='Platform',
                      color='Compiler',
                      color_discrete_map={'intel': '#61D0FF', 'gnu': '#D87327'},
                      text='Number of Tests',
                      height=800, 
                      width=1000,
                      title="Regression Test Framework:<br>Number of Tests vs Platform")
        fig4.update_yaxes(tickfont=dict(family=fontname,
                                        color=txt_color,
                                        size=y_font_sz)
                          #dtick=20
                         )
        fig4.update_xaxes(ticklabelposition='outside bottom',
                          tickfont=dict(family=fontname,
                                        color=txt_color,
                                        size=x_font_sz),
                          categoryorder='category ascending')
        fig4.update_layout(xaxis_title='Platform',
                           legend_title_text='Compiler',
                           title_font_family=fontname,
                           font=dict(size=14),
                           plot_bgcolor=bg_color,
                           paper_bgcolor=bg_color)
        fig4.update_traces(textfont_size=12, 
                           textangle=0,
                           textposition="outside",
                           cliponaxis=False, 
                           marker_line_width=0.1,
                           opacity=1)
        
        # Plot total tests per test-to-platform per compiler per test framework type (OpnReq Framework)
        fig5 = px.bar(df,
                      y='Number of Tests', 
                      x=df.index, 
                      color='Test_Framework_Type',
                      color_discrete_sequence=['#00e06b', '#f56f0a'] ,
                      barmode='group',
                      text='Number of Tests',
                      height=800, 
                      width=1000,
                      title="Number of Tests vs Compiler Environment Across Test Framework")
        fig5.update_yaxes(tickfont=dict(family=fontname,
                                        color=txt_color,
                                        size=y_font_sz)
                          #dtick=20
                         )
        fig5.update_xaxes(ticklabelposition='outside bottom',
                          tickfont=dict(family=fontname,
                                        color=txt_color,
                                        size=x_font_sz))
        fig5.update_layout(xaxis_title='Compiler Environment', 
                           legend_title_text='Test Framework Type',
                           title_font_family=fontname,
                           font=dict(size=14),
                           plot_bgcolor=bg_color,
                           paper_bgcolor=bg_color)
        fig5.update_traces(width=1, 
                           textfont_size=12, 
                           textangle=0,
                           textposition="outside",
                           cliponaxis=False,
                           marker_line_width=0.1,
                           opacity=1)
        # Saving plots
        fig.write_image("plot_results/NumOfTests_vs_Framework-to-Compilers_hg.pdf")
        fig2.write_image("plot_results/RT_NumOfTests_vs-Platform_hg.pdf")
        fig3.write_image("plot_results/Opnreq_NumOfTests_vs_Platform_bar.pdf")
        fig4.write_image("plot_results/RT_NumOfTests_vs_Platform-to-Comp_bar.pdf")
        fig5.write_image("plot_results/NumOfTests_vsCompilerEnvironment_bar.pdf")
        print('Plots saved to local.')

        # Saving plots as json
        fig.write_json("plot_results/NumOfTests_vs_Framework-to-Compilers_hg.json")
        fig2.write_json("plot_results/RT_NumOfTests_vs-Platform_hg.json")
        fig3.write_json("plot_results/Opnreq_NumOfTests_vs_Platform_bar.json")
        fig4.write_json("plot_results/RT_NumOfTests_vs_Platform-to-Comp_bar.json")
        fig5.write_json("plot_results/NumOfTests_vsCompilerEnvironment_bar.json")
        print('JSONs saved to local.')
        
        return
