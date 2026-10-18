import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import re

# =====================================
# 1. PAGE CONFIGURATION
# =====================================

st.set_page_config(
    page_title="Local CSV Insight Agent",
    page_icon="📊",
    layout="wide"
)

# =====================================
# 2. PROFESSIONAL UI
# =====================================

st.markdown("""
<style>
.stApp {
    background-color: #f5f7fb;
}

[data-testid="stSidebar"] {
    background-color: #e8eefb;
}

.block-container {
    padding-top: 2rem;
}

h1 {
    color: #1e3a8a;
}

[data-testid="stMetric"] {
    background-color: white;
    padding: 16px;
    border-radius: 12px;
    border: 1px solid #dbe3f0;
}

.stButton button,
.stDownloadButton button {
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# =====================================
# 3. PROJECT HEADER
# =====================================

st.title("📊 Local CSV Insight Agent")

st.write(
    "Upload your CSV file, analyze your data, "
    "ask questions and generate useful insights."
)

st.caption(
    "Built with Python, Pandas and Streamlit"
)

# =====================================
# 4. CSV UPLOAD
# =====================================

uploaded_file = st.file_uploader(
    "Upload your CSV file",
    type=["csv"]
)

if uploaded_file is None:
    st.info("Please upload a CSV file to get started.")

    st.markdown("""
    ### What can this application do?

    - Analyze numeric data
    - Check missing values
    - Answer basic data questions
    - Search and filter records
    - Create charts
    - Generate downloadable reports
    """)
    st.stop()

# =====================================
# 5. READ CSV
# =====================================

try:
    df = pd.read_csv(uploaded_file)

except Exception as error:
    st.error(f"Unable to read this CSV file: {error}")
    st.stop()

if df.empty or len(df.columns) == 0:
    st.error("The uploaded CSV file is empty.")
    st.stop()

# Remove spaces around column names
df.columns = df.columns.astype(str).str.strip()

numeric_columns = df.select_dtypes(
    include="number"
).columns.tolist()

text_columns = df.select_dtypes(
    include=["object", "string", "category"]
).columns.tolist()

# =====================================
# 6. SIDEBAR NAVIGATION
# =====================================

st.sidebar.title("📊 Navigation")

st.sidebar.write(
    f"Rows: {len(df)} | Columns: {len(df.columns)}"
)

page = st.sidebar.radio(
    "Choose a section",
    [
        "Dashboard",
        "Ask Your CSV",
        "Search & Filter",
        "Charts",
        "Download Report"
    ]
)

# =====================================
# 7. DASHBOARD
# =====================================

if page == "Dashboard":

    st.header("📈 Dashboard")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Records", len(df))
    col2.metric("Total Columns", len(df.columns))
    col3.metric("Numeric Columns", len(numeric_columns))

    st.subheader("Uploaded Data")
    st.dataframe(df, use_container_width=True)

    # Data quality
    st.subheader("🔍 Data Quality Check")

    missing = df.isnull().sum()
    total_missing = int(missing.sum())

    q1, q2 = st.columns(2)

    q1.metric("Missing Values", total_missing)

    q2.metric(
        "Complete Values",
        int(df.size - total_missing)
    )

    if total_missing == 0:
        st.success("No missing values found.")
    else:
        missing_report = pd.DataFrame({
            "Column": missing.index,
            "Missing Values": missing.values
        })

        missing_report = missing_report[
            missing_report["Missing Values"] > 0
        ]

        st.warning("Some columns contain missing values.")
        st.dataframe(
            missing_report,
            use_container_width=True
        )

    # Automatic numeric analysis
    st.subheader("🔢 Automatic Numeric Analysis")

    if numeric_columns:

        for column in numeric_columns:

            with st.container(border=True):
                st.write(f"**{column}**")

                a, b, c, d = st.columns(4)

                a.metric(
                    "Average",
                    round(df[column].mean(), 2)
                )

                b.metric(
                    "Maximum",
                    str(df[column].max())
                )

                c.metric(
                    "Minimum",
                    str(df[column].min())
                )

                d.metric(
                    "Total",
                    round(df[column].sum(), 2)
                )

    else:
        st.info("No numeric columns found.")

    # Student-specific dashboard
    if (
        "Name" in df.columns
        and "Marks" in df.columns
        and pd.api.types.is_numeric_dtype(df["Marks"])
        and df["Marks"].notna().any()
    ):

        st.subheader("🎓 Student Summary")

        marks = df["Marks"]

        a, b, c, d = st.columns(4)

        a.metric("Total Students", len(df))
        b.metric("Average Marks", round(marks.mean(), 2))
        c.metric("Highest Marks", marks.max())
        d.metric("Lowest Marks", marks.min())

        top = df.loc[marks.idxmax()]
        lowest = df.loc[marks.idxmin()]

        st.success(
            f"🏆 Top Student: {top['Name']} "
            f"({top['Marks']} marks)"
        )

        st.info(
            f"Lowest Student: {lowest['Name']} "
            f"({lowest['Marks']} marks)"
        )

    # Automatic insights
    st.subheader("💡 Automatic Insights")

    st.write(f"Your dataset contains **{len(df)} records**.")

    st.write(f"It contains **{len(df.columns)} columns**.")

    if numeric_columns:

        best_column = max(
            numeric_columns,
            key=lambda col: df[col].mean()
            if df[col].notna().any()
            else float("-inf")
        )

        if df[best_column].notna().any():
            st.write(
                f"**{best_column}** has an average of "
                f"**{df[best_column].mean():.2f}**."
            )

    if total_missing > 0:
        st.write(
            f"There are **{total_missing} missing values** "
            "that may need attention."
        )
    else:
        st.write("All cells contain values.")

    if "Department" in df.columns:
        counts = df["Department"].value_counts()

        if not counts.empty:
            st.write(
                f"Most common department/category: "
                f"**{counts.index[0]}** "
                f"({counts.iloc[0]} records)."
            )

# =====================================
# 8. ASK YOUR CSV
# =====================================

elif page == "Ask Your CSV":

    st.header("💬 Ask Your CSV")

    st.write(
        "Ask simple questions about your uploaded data."
    )

    question = st.text_input(
        "Enter your question",
        placeholder="Example: What is the average Marks?",
        key="csv_question"
    )

    if question:

        q = question.lower().strip()
        answered = False

        # Count records
        if (
            "how many rows" in q
            or "how many records" in q
            or "total records" in q
            or "how many students" in q
            or "total students" in q
        ):
            st.success(f"Total records: {len(df)}")
            answered = True

        # Missing values
        elif "missing" in q:
            st.write(
                "Total missing values:",
                int(df.isnull().sum().sum())
            )
            st.dataframe(
                df.isnull().sum().rename(
                    "Missing Values"
                ).to_frame()
            )
            answered = True

        # Find a numeric column mentioned in the question
        selected_numeric = None

        for column in numeric_columns:
            if column.lower() in q:
                selected_numeric = column
                break

        if selected_numeric is None and numeric_columns:
            if "Marks" in df.columns:
                selected_numeric = "Marks"
            else:
                selected_numeric = numeric_columns[0]

        # Filter records above or below a number
        number_match = re.search(
            r"-?\d+(?:\.\d+)?",
            q
        )

        if (
            not answered
            and number_match
            and selected_numeric
            and any(
                word in q
                for word in [
                    "above", "greater", "more than",
                    "below", "less than", "under"
                ]
            )
        ):

            number = float(number_match.group())

            if any(
                word in q
                for word in ["below", "less than", "under"]
            ):
                result = df[
                    df[selected_numeric] < number
                ]
            else:
                result = df[
                    df[selected_numeric] > number
                ]

            st.write(
                f"Found {len(result)} matching records."
            )
            st.dataframe(
                result,
                use_container_width=True
            )
            answered = True

        # Numeric statistics
        if not answered and selected_numeric:

            series = df[selected_numeric].dropna()

            if series.empty:
                st.warning(
                    "This column has no numeric values to analyze."
                )

            elif any(
                word in q
                for word in ["average", "mean"]
            ):
                st.success(
                    f"Average {selected_numeric}: "
                    f"{series.mean():.2f}"
                )

            elif any(
                word in q
                for word in ["highest", "maximum", "maximum value"]
            ) or "top" in q:

                row = df.loc[series.idxmax()]

                if "Name" in df.columns:
                    st.success(
                        f"Highest {selected_numeric}: "
                        f"{row[selected_numeric]} "
                        f"(Student/record: {row['Name']})"
                    )
                else:
                    st.success(
                        f"Maximum {selected_numeric}: "
                        f"{series.max()}"
                    )

            elif any(
                word in q
                for word in ["lowest", "minimum", "minimum value"]
            ):
                row = df.loc[series.idxmin()]

                if "Name" in df.columns:
                    st.success(
                        f"Lowest {selected_numeric}: "
                        f"{row[selected_numeric]} "
                        f"(Student/record: {row['Name']})"
                    )
                else:
                    st.success(
                        f"Minimum {selected_numeric}: "
                        f"{series.min()}"
                    )

            elif any(
                word in q
                for word in ["total", "sum"]
            ):
                st.success(
                    f"Total {selected_numeric}: "
                    f"{series.sum():.2f}"
                )

            else:
                st.info(
                    "Try asking about average, highest, "
                    "lowest, total, or filtering by a number."
                )

            answered = True

        # Department/category lookup
        if not answered:

            matched_category = None

            for column in text_columns:
                for value in df[column].dropna().unique():

                    value_text = str(value).strip()

                    if (
                        value_text
                        and value_text.lower() in q
                    ):
                        matched_category = (
                            column,
                            value_text
                        )
                        break

                if matched_category:
                    break

            if matched_category:

                column, value = matched_category

                result = df[
                    df[column].astype(str).str.lower()
                    == value.lower()
                ]

                st.write(
                    f"Records matching {value}: {len(result)}"
                )
                st.dataframe(
                    result,
                    use_container_width=True
                )
                answered = True

        if not answered:
            st.warning(
                "I could not understand that question. "
                "Try asking about average, maximum, minimum, "
                "total records, missing values, or a category."
            )

    st.caption(
        "Note: This version uses keyword-based rules, "
        "not a full AI language model."
    )

# =====================================
# 9. SEARCH AND FILTER
# =====================================

elif page == "Search & Filter":

    st.header("🔎 Search & Filter")

    search_column = st.selectbox(
        "Choose a column to search",
        df.columns.tolist(),
        key="search_column"
    )

    search_text = st.text_input(
        "Enter search value",
        key="search_text"
    )

    result = df.copy()

    if search_text:
        result = result[
            result[search_column].astype(str).str.contains(
                search_text,
                case=False,
                na=False
            )
        ]

    if "Department" in df.columns:

        departments = (
            df["Department"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        selected_department = st.selectbox(
            "Filter by Department",
            ["All"] + departments,
            key="department_filter"
        )

        if selected_department != "All":
            result = result[
                result["Department"].astype(str)
                == selected_department
            ]

    st.write(f"Matching records: {len(result)}")

    st.dataframe(
        result,
        use_container_width=True
    )

# =====================================
# 10. ADVANCED CHARTS
# =====================================

elif page == "Charts":

    st.header("📊 Data Visualization")

    if not numeric_columns:
        st.warning(
            "Your CSV needs at least one numeric column "
            "to create these charts."
        )
        st.stop()

    chart_type = st.selectbox(
        "Choose chart type",
        [
            "Bar Chart",
            "Line Chart",
            "Pie Chart",
            "Histogram"
        ]
    )

    selected_column = st.selectbox(
        "Choose numeric column",
        numeric_columns,
        key="selected_chart_column"
    )

    if chart_type == "Bar Chart":

        st.subheader(f"Bar Chart: {selected_column}")

        st.bar_chart(df[selected_column])

    elif chart_type == "Line Chart":

        st.subheader(f"Line Chart: {selected_column}")

        st.line_chart(df[selected_column])

    elif chart_type == "Pie Chart":

        counts = df[selected_column].dropna().value_counts()

        if counts.empty:
            st.warning("No values available for this chart.")
        else:
            fig, ax = plt.subplots()

            ax.pie(
                counts.values,
                labels=counts.index.astype(str),
                autopct="%1.1f%%"
            )

            ax.set_title(f"Distribution of {selected_column}")

            st.pyplot(fig)
            plt.close(fig)

    elif chart_type == "Histogram":

        values = df[selected_column].dropna()

        if values.empty:
            st.warning("No values available for this chart.")
        else:
            fig, ax = plt.subplots()

            ax.hist(
                values,
                bins=10,
                edgecolor="black"
            )

            ax.set_xlabel(selected_column)
            ax.set_ylabel("Frequency")
            ax.set_title(f"Histogram of {selected_column}")

            st.pyplot(fig)
            plt.close(fig)

    # Department chart
    if "Department" in df.columns:

        st.subheader("Department Analysis")

        department_counts = df["Department"].value_counts()

        st.bar_chart(department_counts)

# =====================================
# 11. DOWNLOAD REPORT
# =====================================

elif page == "Download Report":

    st.header("📥 Download Analysis Report")

    report_rows = []

    report_rows.append({
        "Metric": "Total Records",
        "Value": len(df)
    })

    report_rows.append({
        "Metric": "Total Columns",
        "Value": len(df.columns)
    })

    report_rows.append({
        "Metric": "Total Missing Values",
        "Value": int(df.isnull().sum().sum())
    })

    for column in numeric_columns:

        report_rows.extend([
            {
                "Metric": f"{column} Average",
                "Value": round(df[column].mean(), 2)
            },
            {
                "Metric": f"{column} Maximum",
                "Value": df[column].max()
            },
            {
                "Metric": f"{column} Minimum",
                "Value": df[column].min()
            },
            {
                "Metric": f"{column} Total",
                "Value": round(df[column].sum(), 2)
            }
        ])

    report = pd.DataFrame(report_rows)

    st.subheader("Report Preview")

    st.dataframe(
        report,
        use_container_width=True
    )

    csv_report = report.to_csv(index=False)

    st.download_button(
        label="⬇️ Download Analysis Report",
        data=csv_report,
        file_name="csv_analysis_report.csv",
        mime="text/csv",
        key="report_download"
    )

    st.caption(
        "The report contains summary statistics, "
        "not the complete original dataset."
    )

# =====================================
# 12. FOOTER
# =====================================

st.sidebar.divider()

st.sidebar.caption(
    "Local CSV Insight Agent | Python + Pandas + Streamlit"
)