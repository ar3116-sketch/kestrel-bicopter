# Neutral-installation wire schedule

Lengths follow modeled centerlines. Cut lengths add 15 mm termination allowance and 20 mm additional slack on each motor phase extension. Hand dress and measure before cutting final wires; routes are not a flexible harness simulation.

| Wire | Net | AWG | Route mm | Cut allowance mm | Endpoint functions |
|---|---|---:|---:|---:|---|
| L_ESC_VBAT | VBAT | 18 | 22 | 37 | Power splice + → ESC L + |
| L_ESC_GND | GND | 18 | 17 | 33 | Power splice - → ESC L - |
| L_Phase_0 | PHASE_L0 | 18 | 148 | 183 | ESC L phase0 → Motor L phase0 |
| L_Phase_1 | PHASE_L1 | 18 | 146 | 182 | ESC L phase1 → Motor L phase1 |
| L_Phase_2 | PHASE_L2 | 18 | 146 | 181 | ESC L phase2 → Motor L phase2 |
| L_Servo_0 | SERVO_L | 24 | 76 | 91 | Servo L → FC S9/S10 |
| L_Servo_1 | 6V_SERVO | 24 | 65 | 81 | Servo L → UBEC output |
| L_Servo_2 | GND | 24 | 66 | 82 | Servo L → UBEC output |
| L_ESC_signal | ESC_L | 26 | 30 | 45 | FC S1/S2 → ESC L signal |
| L_ESC_signal_ground | GND | 26 | 32 | 47 | FC GND → ESC L signal GND |
| R_ESC_VBAT | VBAT | 18 | 22 | 37 | Power splice + → ESC R + |
| R_ESC_GND | GND | 18 | 23 | 38 | Power splice - → ESC R - |
| R_Phase_0 | PHASE_R0 | 18 | 148 | 183 | ESC R phase0 → Motor R phase0 |
| R_Phase_1 | PHASE_R1 | 18 | 146 | 182 | ESC R phase1 → Motor R phase1 |
| R_Phase_2 | PHASE_R2 | 18 | 146 | 181 | ESC R phase2 → Motor R phase2 |
| R_Servo_0 | SERVO_R | 24 | 76 | 91 | Servo R → FC S9/S10 |
| R_Servo_1 | 6V_SERVO | 24 | 65 | 81 | Servo R → UBEC output |
| R_Servo_2 | GND | 24 | 66 | 82 | Servo R → UBEC output |
| R_ESC_signal | ESC_R | 26 | 30 | 45 | FC S1/S2 → ESC R signal |
| R_ESC_signal_ground | GND | 26 | 32 | 47 | FC GND → ESC R signal GND |
| Battery_stock_positive | VBAT | 14 | 14 | 29 | B1 pack + → XT60 battery half + |
| Battery_stock_negative | GND | 14 | 14 | 29 | B1 pack - → XT60 battery half - |
| B1_positive | VBAT | 14 | 121 | 137 | XT60 + → Power splice + |
| B1_negative | GND | 14 | 121 | 137 | XT60 - → Power splice - |
| UBEC_input_0 | VBAT | 22 | 104 | 119 | Power splice → UBEC input |
| FC_input_0 | VBAT | 26 | 35 | 51 | Power splice → FC battery input |
| Capacitor_0 | VBAT | 24 | 114 | 129 | Power splice → C1 |
| UBEC_input_1 | GND | 22 | 113 | 128 | Power splice → UBEC input |
| FC_input_1 | GND | 26 | 34 | 50 | Power splice → FC battery input |
| Capacitor_1 | GND | 24 | 118 | 134 | Power splice → C1 |
| Receiver_0 | 5V_FC | 26 | 25 | 41 | RP1 5V → FC 5V |
| Receiver_1 | GND | 26 | 25 | 41 | RP1 GND → FC GND |
| Receiver_2 | CRSF_TX | 26 | 25 | 41 | RP1 TX → FC RX2 |
| Receiver_3 | CRSF_RX | 26 | 25 | 41 | RP1 RX → FC TX2 |
| Balance_0 | CELL_TAP_0 | 26 | 19 | 35 | B1 balance tap → J2 pin 1 |
| Balance_1 | CELL_TAP_1 | 26 | 19 | 35 | B1 balance tap → J2 pin 2 |
| Balance_2 | CELL_TAP_2 | 26 | 19 | 35 | B1 balance tap → J2 pin 3 |
| Balance_3 | CELL_TAP_3 | 26 | 19 | 35 | B1 balance tap → J2 pin 4 |
| Balance_4 | CELL_TAP_4 | 26 | 19 | 35 | B1 balance tap → J2 pin 5 |
| Antenna_coax | RF | 30 | 75 | 90 | RP1 UFL → T antenna |
| Buzzer_wire_0 | BUZZER+ | 26 | 64 | 79 | Buzzer → FC buzzer pad |
| Buzzer_wire_1 | BUZZER- | 26 | 64 | 79 | Buzzer → FC buzzer pad |
