#ifndef LMMS_AGENT_CONTROL_VIEW_H
#define LMMS_AGENT_CONTROL_VIEW_H

#include <QTextEdit>
#include <QLineEdit>
#include <QLabel>
#include <QPushButton>
#include <QProcess>

#include "ToolPluginView.h"

namespace lmms
{
class AgentControlPlugin;

namespace gui
{

class AgentControlView : public ToolPluginView
{
	Q_OBJECT
public:
	explicit AgentControlView( AgentControlPlugin *plugin );

private slots:
	void runCommand();
	void appendLog( const QString &text );
	void startVoiceCapture();
	void stopVoiceCapture();
	void voiceProcessError( QProcess::ProcessError error );

private:
	void setVoiceUiState( bool recording );
	QString ffmpegPath() const;
	QString whisperPath() const;
	QString microphoneDevice() const;
	QStringList ffmpegCaptureArgs( const QString &outputPath ) const;
	bool runWhisperAndDispatch( const QString &audioPath );

	AgentControlPlugin *m_plugin;
	QLineEdit *m_input;
	QTextEdit *m_log;
	QLabel *m_status;
	QPushButton *m_voiceStartButton;
	QPushButton *m_voiceStopButton;
	QProcess *m_voiceRecordProcess;
	QString m_voiceAudioPath;
};

} // namespace gui

} // namespace lmms

#endif // LMMS_AGENT_CONTROL_VIEW_H
