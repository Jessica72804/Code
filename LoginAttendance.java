import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;

public class LoginAttendance {
    public static void main(String[] args){

        JFrame loginFrame=new JFrame();
        loginFrame.setTitle("Login Form");
        loginFrame.setSize(400, 280);
        loginFrame.setLocationRelativeTo(null);
        loginFrame.setLayout(null);

        JPanel loginPanel=new JPanel();
        loginPanel.setLayout(null);
        loginPanel.setBackground(Color.white);
        loginPanel.setBounds(20,20,350,200);

        JLabel usernameLabel=new JLabel("Username");
        usernameLabel.setFont(new Font("Segoe UI", Font.PLAIN, 14));
        usernameLabel.setBounds(30, 30, 80, 25);

        JLabel passLabel=new JLabel("Password");
        passLabel.setFont(new Font("Segoe UI", Font.PLAIN, 14));
        passLabel.setBounds(30, 70, 80, 25);

        JTextField userInput=new JTextField();
        userInput.setBounds(120,30,180,25);

        JPasswordField passwordInput=new JPasswordField();
        passwordInput.setBounds(120,70,180,25);

        JButton loginBtn=new JButton("Log in");
        loginBtn.setBounds(70,120,90,30);

        JButton cancelBtn=new JButton("Cancel");
        cancelBtn.setBounds(180,120,90,30);

        loginBtn.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                String username=userInput.getText();
                String password=String.valueOf(passwordInput.getPassword());
                if(username.equals("Teacher1") && password.equals("12345")){
                    JOptionPane.showMessageDialog(loginFrame,"Login Successfully!");
                    loginFrame.dispose();
                    showAttendance();
                } else {
                    JOptionPane.showMessageDialog(loginFrame, "Invalid Username/Password");
                }
            }
        });

        cancelBtn.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e){
                userInput.setText(null);
                passwordInput.setText(null);  
            }
        });

        loginFrame.add(cancelBtn);
        loginFrame.add(loginBtn);
        loginFrame.add(passwordInput);
        loginFrame.add(userInput);
        loginFrame.add(passLabel);
        loginFrame.add(usernameLabel);
        loginFrame.add(loginPanel);
        loginFrame.setVisible(true);
        loginFrame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);

    }

    public static void showAttendance() {
        JFrame attendancFrame = new JFrame();
        attendancFrame.setTitle("Attendance Record System");
        attendancFrame.setSize(520, 500);
        attendancFrame.setLocationRelativeTo(null);
        attendancFrame.setLayout(null);
       
        JPanel attendancePanel = new JPanel();
        attendancePanel.setLayout(null);
        attendancePanel.setBackground(Color.WHITE);
        attendancePanel.setBounds(20, 20, 460, 420);

        JLabel nameLabel = new JLabel("Enter Name: ");
        nameLabel.setFont(new Font("Segoe UI", Font.PLAIN, 14));
        nameLabel.setBounds(30, 30, 100, 25);

        JTextField nameInput = new JTextField();
        nameInput.setBounds(130, 30, 280, 25);

        JButton presentBtn = new JButton("Present");
        presentBtn.setBounds(130, 70, 100, 30);

        JButton absentBtn = new JButton("Absent");
        absentBtn.setBounds(250, 70, 100, 30);

        JTextArea recordArea = new JTextArea();
        recordArea.setEditable(false);
        recordArea.setFont(new Font("Monospaced", Font.PLAIN, 12));

        JScrollPane scrollPane = new JScrollPane(recordArea);
        scrollPane.setBounds(30, 120, 380, 200);

        JButton saveBtn = new JButton("Save");
        saveBtn.setBounds(30, 340, 150, 30);

        ArrayList<String> records = new ArrayList<>();
        int[] count = {0};

        ActionListener markAttendance = new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                String name = nameInput.getText().trim();
                if (name.isEmpty()) {
                    JOptionPane.showMessageDialog(attendancFrame, "Please enter a name.");
                    return;
                }

                String status = e.getActionCommand();
                count[0]++;
                String dateTime = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm"));
                String record = count[0] + ". " + name + " - " + status + " [" + dateTime + "]";
                records.add(record);
                recordArea.append(record + "\n");
                nameInput.setText("");
            }
        };

        presentBtn.addActionListener(markAttendance);
        absentBtn.addActionListener(markAttendance);

        saveBtn.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                try {
                    if (recordArea.getText().isEmpty()) {
                        JOptionPane.showMessageDialog(attendancFrame, "No attendance record to save.");
                        return;
                    }

                    java.io.FileWriter writer = new java.io.FileWriter("attendance_records.txt");
                    writer.write(recordArea.getText());
                    writer.close();
                    JOptionPane.showMessageDialog(attendancFrame, "Attendance saved successfully!");
                } catch (Exception ex) {
                    JOptionPane.showMessageDialog(attendancFrame, "Error saving file: " + ex.getMessage());
                }
            }
        });

        attendancePanel.add(nameLabel);
        attendancePanel.add(nameInput);
        attendancePanel.add(presentBtn);
        attendancePanel.add(absentBtn);
        attendancePanel.add(scrollPane);
        attendancePanel.add(saveBtn);
        attendancFrame.add(attendancePanel);

        attendancFrame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        attendancFrame.setVisible(true);
    }
}
