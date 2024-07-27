function filterByGrade() {
            var gradeFilter = document.getElementById('gradeFilter').value;
            var table = document.getElementById('studentTable');
            // var tbody = table.getElementsByTagName('tbody')[0];
            // var rows = tbody.getElementsByTagName('tr');
            var rows = document.getElementsByClassName('student');


            for (var i = 0; i < rows.length; i++) {
                var grade = rows[i].getElementsByClassName('years_old')[0].innerText.trim();
                if (gradeFilter === 'all' || grade === gradeFilter) {
                    rows[i].style.display = 'table-row';
                } else {
                    rows[i].style.display = 'none';
                }
            }
        }