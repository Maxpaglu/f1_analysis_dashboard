import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import base64

# Function to load qualifying dataset based on selected year
@st.cache_data

def load_qualifying_data(year):
    file_paths = {
        "2022": r'data/Formula1_2022season_qualifyingResults.csv',
        "2023": r'data/Formula1_2023season_qualifyingResults.csv',
        "2024": r'data/Formula1_2024season_qualifyingResults.csv',
        "2025": r'data/Formula1_2025season_qualifyingResults.csv'
    }
    try:
        if year in file_paths:
            return pd.read_csv(file_paths[year])
    except Exception as e:
        st.error(f"Error loading qualifying data for {year}: {e}")
    return None

# Function to load race dataset based on selected year
@st.cache_data

def load_race_data(year):
    file_paths = {
        "2022": r'data/Formula1_2022season_raceResults.csv',
        "2023": r'data/Formula1_2023season_raceResults.csv',
        "2024": r'data/Formula1_2024season_raceResults.csv',
        "2025": r'data/Formula1_2025Season_RaceResults.csv'
    }
    try:
        if year in file_paths:
            return pd.read_csv(file_paths[year])
    except Exception as e:
        st.error(f"Error loading race data for {year}: {e}")
    return None

# Convert qualifying times (Q1, Q2, Q3) into seconds for easier comparison
def convert_to_seconds(time_str):
    if pd.isna(time_str) or not isinstance(time_str, str):
        return None
    time_str = time_str.strip()
    if ':' in time_str:
        try:
            minutes, seconds = time_str.split(':')
            return int(minutes) * 60 + float(seconds)
        except ValueError:
            return None
    try:
        return float(time_str)  
    except ValueError:
        return None


def main():
    # Tabs
    tab1, tab2, tab3 = st.tabs(["Home", "Drivers Quali Comparisons", "Race Performance of Drivers"])

    with tab1:
        # logo_path = r"C:\Users\DELL\Desktop\dsbda\images\download.png"
        # st.image(logo_path, width=150)

        st.markdown("""
        <h1 style='text-align: center;'>An Maximus Analysis</h1>
        <h2 style='text-align: center;'>Formula 1 Qualifying Dashboard</h2>
        <h2 style='text-align: left;'>"Welcome to the Ultimate F1 Analysis Dashboard – Dive into real-time race insights, driver performance metrics, and historical trends that define the pinnacle of motorsport!"</h2>
        """, unsafe_allow_html=True)

        home_image_path = r'images/download.png'
        st.image(home_image_path, use_container_width=True)

    with tab2:
        st.subheader("Drivers Quali Comparisons")
        sub_tab = st.radio("Select Analysis Type", ["Track Comparisons", "Driver Quali Position Over Season", "Team Pole Position Comparison"])

        year = st.selectbox("Select Season", ["2022", "2023", "2024", "2025"])
        df = load_qualifying_data(year)
        if df is None:
            st.warning("No data found for the selected season.")
            return

        if sub_tab == "Track Comparisons":
            tracks = df['Track'].unique()
            selected_track = st.selectbox('Select Track', tracks, index=0)
            filtered_data = df[df['Track'] == selected_track].copy()

            for session in ['Q1', 'Q2', 'Q3']:
                filtered_data[f'{session}_seconds'] = filtered_data[session].apply(convert_to_seconds)

            filtered_data.dropna(subset=['Q1_seconds', 'Q2_seconds', 'Q3_seconds'], inplace=True)
            if filtered_data.empty:
                st.write("No data available for the selected track.")
                return

            st.subheader(f"Qualifying Results at {selected_track} - {year} Season")
            st.dataframe(filtered_data.sort_values(by='Q3_seconds').drop(columns=['Track'], errors='ignore'))

            if st.button("Show Qualifying Times Graph"):
                plot_data = filtered_data.melt(id_vars=['Driver'], value_vars=['Q1_seconds', 'Q2_seconds', 'Q3_seconds'],
                                               var_name='Session', value_name='Time')

                if not plot_data.empty:
                    fig, ax = plt.subplots(figsize=(12, 6))
                    for driver in filtered_data['Driver'].unique():
                        driver_data = plot_data[plot_data['Driver'] == driver]
                        sns.lineplot(data=driver_data, x='Session', y='Time', label=driver, ax=ax, marker='o')
                    ax.set_title(f"Comparing All Drivers' Qualifying Times at {selected_track} - {year} Season")
                    ax.set_xlabel('Session (Q1, Q2, Q3)')
                    ax.set_ylabel('Time (Seconds)')
                    ax.legend(title="Driver", bbox_to_anchor=(1.02, 1), loc="upper left", borderaxespad=0)
                    ax.grid(True, linestyle="--", alpha=0.7)
                    st.pyplot(fig)

        elif sub_tab == "Driver Quali Position Over Season":
            drivers = df['Driver'].unique()
            selected_driver = st.selectbox("Select Driver", drivers)
            driver_data = df[df['Driver'] == selected_driver].copy()
            driver_data = driver_data[['Track', 'Position']].sort_values(by='Track')

            fig = px.line(driver_data, x='Track', y='Position', markers=True, title=f"Qualifying Position Over the Season - {selected_driver}")
            fig.update_yaxes(autorange='reversed', dtick=1, title_text="Qualifying Position", range=[1, 20])
            fig.update_xaxes(title_text="Race (Track)")
            st.plotly_chart(fig)

        elif sub_tab == "Team Pole Position Comparison":
            st.subheader("Compare Team Pole Positions")
            team_pole_counts = df[df['Position'] == 1]['Team'].value_counts()
            fig = px.pie(values=team_pole_counts, names=team_pole_counts.index, title="Pole Position Distribution Among Teams", hole=0.4)
            st.plotly_chart(fig)

    with tab3:
        st.subheader("Race Performance of Drivers")

        year = st.selectbox("Select Race Performance Season", ["2022", "2023", "2024", "2025"], key="race_perf")
        race_df = load_race_data(year)

        if race_df is None or 'Position' not in race_df.columns:
            st.warning("No race data available for this season.")
            return

        race_sub_tab = st.radio("Select Race Performance View", ["Individual Driver Stats", "Grid vs Final Position Comparison"])

        if race_sub_tab == "Individual Driver Stats":
            driver_list = race_df['Driver'].unique()
            selected_driver = st.selectbox("Select Driver", driver_list, key="race_driver")
            race_driver_df = race_df[race_df['Driver'] == selected_driver].copy()

            columns_to_show = ['Track', 'Starting Grid', 'Position', 'Laps', 'Points', 'Set Fastest Lap', 'Fastest Lap Time']
            available_columns = [col for col in columns_to_show if col in race_driver_df.columns]
            st.dataframe(race_driver_df[available_columns])

            fig = px.line(race_driver_df, x='Track', y='Position', markers=True,
                          title=f"Race Finishing Positions Over the Season - {selected_driver}")
            fig.update_yaxes(autorange='reversed', dtick=1, title_text="Race Finish Position")
            fig.update_xaxes(title_text="Track")
            st.plotly_chart(fig)

        elif race_sub_tab == "Grid vs Final Position Comparison":
            st.subheader("Grid vs Final Position (Track-wise)")
            selected_track = st.selectbox("Select Track for Comparison", race_df['Track'].unique(), key="track_grid_vs_position")
            track_data = race_df[race_df['Track'] == selected_track].copy()

            if 'Starting Grid' in track_data.columns and 'Position' in track_data.columns:
                plot_df = track_data[['Driver', 'Starting Grid', 'Position']].melt(id_vars='Driver',
                                                                                   value_vars=['Starting Grid', 'Position'],
                                                                                   var_name='Stage',
                                                                                   value_name='Position Value')

                fig = px.line(plot_df, x='Driver', y='Position Value', color='Stage', markers=True,
                              title=f"Starting Grid vs Finishing Position - {selected_track}")
                fig.update_layout(yaxis=dict(autorange='reversed', title='Position'), xaxis_title='Driver')
                st.plotly_chart(fig)
            else:
                st.write("Required columns not found in dataset.")

if __name__ == '__main__':
    main()
