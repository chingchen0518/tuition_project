function filterByGrade() {
            var gradeFilter = document.getElementById('gradeFilter').value;
            var yearFilter = document.getElementById('yearFilter').value;
            var rows = document.getElementsByClassName('classes');



            for (var i = 0; i < rows.length; i++) {
                var grade = rows[i].getElementsByClassName('years_old')[0].innerText.trim();
                var year = rows[i].getElementsByClassName('year')[0].innerText.trim();
                console.log(grade)
                if (gradeFilter === 'all' && yearFilter==='all') {
                    rows[i].style.display = 'block';
                } else if(gradeFilter === 'all' && yearFilter===year){
                    rows[i].style.display = 'block';
                } else if(grade === gradeFilter && yearFilter==='all'){
                    rows[i].style.display = 'block';
                } else if(grade === gradeFilter && yearFilter===year){
                    rows[i].style.display = 'block';
                } else {
                    rows[i].style.display = 'none';
                }
            }
        }